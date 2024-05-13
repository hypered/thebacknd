/// Command-line definition for thebacknd client binary.
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    version = "0.1.0",
    author = "Võ Minh Thu <thu@hypered.io>",
    about = "Ephemeral virtual machines in the cloud in one command"
)]
pub struct Cli {
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
    /// The full path to a binary or toplevel store path
    pub full_path: Option<String>,

    /// Enable verbose output
    #[arg(short, long)]
    pub verbose: bool,
}
