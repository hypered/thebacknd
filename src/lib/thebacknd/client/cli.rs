/// Command-line definition for thebacknd client binary.
use clap::{Parser, Subcommand};
use clap_complete::{Shell};

#[derive(Parser)]
#[command(
    version = "0.1.0",
    author = "Võ Minh Thu <thu@hypered.io>",
    about = "Ephemeral virtual machines in the cloud in one command"
)]
pub struct Cli {
    // If provided, outputs the completion file for given shell
    #[arg(long = "generate", value_enum)]
    pub generator: Option<Shell>,
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    Run(RunCmd),
}

/// Run a toplevel or a binary in a cloud virtual machine
#[derive(Parser)]
pub struct RunCmd {
    /// The full path to a binary or toplevel store path, or to a Nix file (when an attribute is
    /// given).
    pub full_path: Option<String>,

    /// The attribute path to build
    #[arg(short = 'A', long)]
    pub attr: Option<String>,

    /// Enable verbose output
    #[arg(short, long)]
    pub verbose: bool,
}
