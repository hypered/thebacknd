/// Command-line definition for thebacknd agent binary (called thewithn).
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "thewithn")]
#[command(about = "A program that behaves differently based on the symlink name or subcommands")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
}

#[derive(Subcommand)]
pub enum Commands {
    CurrentSystem(CurrentSystemCmd),
    DesiredSystem(DesiredSystemCmd),
    DestroySystem(DestroySystemCmd),
    UpdateSystem(UpdateSystemCmd),
}

#[derive(Parser)]
pub struct CurrentSystemCmd {
}

#[derive(Parser)]
pub struct DesiredSystemCmd {
    /// Provide a custom message
    #[arg(short, long, default_value = "Called as 'desired-system'.")]
    pub message: String,
}

#[derive(Parser)]
pub struct DestroySystemCmd {
    /// Print extra details
    #[arg(short, long)]
    pub details: bool,
}

#[derive(Parser)]
pub struct UpdateSystemCmd {
}
