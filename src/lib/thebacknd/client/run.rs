/// Implement thebacknd CLI.
use std::process::{Command as ProcessCommand, exit};
use regex::Regex;

use super::cli::{RunCmd};

pub fn handle_run(args: &RunCmd) {
    let RunCmd{ full_path, verbose } = args;
    if let Some(full_path) = full_path {
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
