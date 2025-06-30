#![allow(unused_imports)]

mod keybinds;
mod monitors;
mod layouts;
mod tags;

use std::sync::Arc;
use std::sync::Mutex;

use pinnacle_api::input;
use pinnacle_api::input::Bind;
use pinnacle_api::input::Keysym;
use pinnacle_api::input::{Mod, MouseButton};
use pinnacle_api::layout;
use pinnacle_api::layout::generators::Corner;
use pinnacle_api::layout::generators::CornerLocation;
use pinnacle_api::layout::generators::Cycle;
use pinnacle_api::layout::generators::Dwindle;
use pinnacle_api::layout::generators::Fair;
use pinnacle_api::layout::generators::MasterSide;
use pinnacle_api::layout::generators::MasterStack;
use pinnacle_api::layout::generators::Spiral;
use pinnacle_api::layout::LayoutGenerator;
use pinnacle_api::layout::LayoutNode;
use pinnacle_api::layout::LayoutResponse;
use pinnacle_api::output;
use pinnacle_api::pinnacle;
use pinnacle_api::pinnacle::Backend;
use pinnacle_api::process::Command;
use pinnacle_api::signal::OutputSignal;
use pinnacle_api::signal::WindowSignal;
use pinnacle_api::tag;
use pinnacle_api::util::{Axis, Batch};
use pinnacle_api::window;

pub const TERMINAL: &str = "kitty";

async fn config() {
    // Change the mod key to `Alt` when running as a nested window.
    let mod_key = match pinnacle::backend() {
        Backend::Tty => Mod::SUPER,
        Backend::Window => Mod::ALT,
    };
    
    keybinds::keybinds(mod_key).await;

    // Fastttttttt typing!!!
    input::set_repeat_rate(50, 200);
    
    tags::tags(mod_key).await;
    
    layouts::layouts(mod_key).await;

    monitors::monitors().await;

    #[cfg(feature = "snowcap")]
    if let Some(error) = pinnacle_api::pinnacle::take_last_error() {
        // Show previous crash messages
        pinnacle_api::snowcap::ConfigCrashedMessage::new().show(error);
    } else {
        // Or show the bind overlay on startup
        pinnacle_api::snowcap::BindOverlay::new().show();
    }

    // Run when Pinnacle starts
    Command::new(TERMINAL).once().spawn();
    Command::new("swaybg").args(["--mode", "fill", "-i", "/home/chiya/Pictures/Anime/ff/GnW9atrb0AAFJ2J_wallpaper.jpg"]).spawn();
}

pinnacle_api::main!(config);
