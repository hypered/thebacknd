/// Implement thebacknd CLI.
use std::process::{Command as ProcessCommand, exit};
use std::str;
use regex::Regex;

use super::cli::{RunCmd};

pub fn handle_run(args: &RunCmd) {
    let RunCmd{ full_path, attr, verbose } = args;
    if let Some(attr) = attr {
        let full_path = full_path.clone().unwrap_or("default.nix".to_string());
        let store_path = build_nix_attr(&full_path, &attr, *verbose);

        sign_store_path(&store_path, *verbose);
        cache_store_path(&store_path, *verbose);

        let param = format!("nix_toplevel:{}", store_path);
        invoke_create(Some(&param), *verbose);
    } else if let Some(full_path) = full_path {
        let re = Regex::new(r"(/nix/store/[^/]+)/.+").unwrap();
        let store_path = re.captures(full_path)
            .map(|caps| caps.get(1).unwrap().as_str())
            .unwrap_or(full_path);

        let param = if full_path == store_path {
            format!("nix_toplevel:{}", store_path)
        } else {
            format!("nix_binary:{}", full_path)
        };

        invoke_create(Some(&param), *verbose);
    } else {
        invoke_create(None, *verbose);
    }
}

fn build_nix_attr(nix_file: &str, attr: &str, verbose: bool) -> String {
    let mut command = ProcessCommand::new("nix-build");
    command.args(&[nix_file, "--attr", attr]);

    if verbose {
        println!("Executing: {:?}", command);
    }

    let output = command
        .output()
        .expect("Failed to execute nix-build command");

    if !output.status.success() {
        println!("Command failed with error: {}", str::from_utf8(&output.stderr).unwrap_or("Unknown error"));
        exit(output.status.code().unwrap_or(1));
    }

    // Return the first line of stdout
    let first_line = str::from_utf8(&output.stdout)
        .unwrap_or("")
        .lines()
        .next()
        .unwrap_or("")
        .to_string();

    if !first_line.starts_with("/nix/store") {
        eprintln!("Error: Expected output to start with '/nix/store', got: {}", first_line);
        exit(1);
    }

    first_line
}

fn sign_store_path(store_path: &str, verbose: bool) {
    let mut command = ProcessCommand::new("nix");
    command.args(&["store", "sign", "--recursive", "--key-file", "../thebacknd/signing-keys/cache-priv-key.pem", store_path]);

    if verbose {
        println!("Executing: {:?}", command);
    }

    let status = command
        .status()
        .expect("Failed to execute nix store sign command");

    if !status.success() {
        exit(status.code().unwrap_or(1));
    }
}

fn cache_store_path(store_path: &str, verbose: bool) {
    let mut command = ProcessCommand::new("nix");
    command.args(&["copy", "--to", "s3://hypered-private-store/cache?endpoint=s3.eu-central-003.backblazeb2.com", store_path]);

    if verbose {
        println!("Executing: {:?}", command);
    }

    let status = command
        .status()
        .expect("Failed to execute nix copy --to command");

    if !status.success() {
        exit(status.code().unwrap_or(1));
    }
}

/// Call the `thebacknd/create` serverless function using the `doctl` command-line tool.
fn invoke_create(param: Option<&str>, verbose: bool) {
    let mut command = ProcessCommand::new("doctl");
    command.args(&["serverless", "functions", "invoke", "thebacknd/create"]);

    if let Some(param) = param {
        command.args(&["--param", param]);
    }

    if verbose {
        println!("Executing: {:?}", command);
    }

    let status = command
        .status()
        .expect("Failed to execute doctl command");

    if !status.success() {
        exit(status.code().unwrap_or(1));
    }
}
