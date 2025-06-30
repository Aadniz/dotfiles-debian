#![allow(unused_imports)]

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

pub async fn monitors(){
    // Monitor setup
    if let Some(left_monitor) = output::get_by_name("HDMI-A-1") {
        left_monitor.set_loc(0, 0);
        left_monitor.set_mode(2560, 1440, 119998);
    }
    if let Some(middle_monitor) = output::get_by_name("DP-3") {
        middle_monitor.set_loc(2560, 0);
        middle_monitor.set_mode(2560, 1440, 165000);

    }
    if let Some(right_monitor) = output::get_by_name("eDP-1") {
        right_monitor.set_scale(2.0);
        right_monitor.set_loc(5120, 720);
        right_monitor.set_mode(2880, 1800, 90001);
    }
}