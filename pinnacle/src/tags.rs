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

pub const TAG_NAMES: [&str; 10] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"];

pub async fn tags(mod_key: Mod) {
    //------------------------
    // Tags                  |
    //------------------------

    // Setup all monitors with tags "1" through "9"
    output::for_each_output(move |output| {
        let mut tags = tag::add(output, TAG_NAMES);
        tags.next().unwrap().set_active(true);
    });

    for tag_name in TAG_NAMES {
        // `mod_key + 1-9` switches to tag "1" to "9"
        input::keybind(mod_key, tag_name)
            .on_press(move || {
                if let Some(tag) = tag::get(tag_name) {
                    tag.switch_to();
                }
            })
            .group("Tag")
            .description(format!("Switch to tag {tag_name}"));

        // `mod_key + ctrl + 1-9` toggles tag "1" to "9"
        input::keybind(mod_key | Mod::CTRL, tag_name)
            .on_press(move || {
                if let Some(tag) = tag::get(tag_name) {
                    tag.toggle_active();
                }
            })
            .group("Tag")
            .description(format!("Toggle tag {tag_name}"));

        // `mod_key + shift + 1-9` moves the focused window to tag "1" to "9"
        input::keybind(mod_key | Mod::SHIFT, tag_name)
            .on_press(move || {
                if let Some(tag) = tag::get(tag_name) {
                    if let Some(win) = window::get_focused() {
                        win.move_to_tag(&tag);
                    }
                }
            })
            .group("Tag")
            .description(format!("Move the focused window to tag {tag_name}"));

        // `mod_key + ctrl + shift + 1-9` toggles tag "1" to "9" on the focused window
        input::keybind(mod_key | Mod::CTRL | Mod::SHIFT, tag_name)
            .on_press(move || {
                if let Some(tg) = tag::get(tag_name) {
                    if let Some(win) = window::get_focused() {
                        win.toggle_tag(&tg);
                    }
                }
            })
            .group("Tag")
            .description(format!("Toggle tag {tag_name} on the focused window"));
    }

    input::libinput::for_each_device(|device| {
        // Enable natural scroll for touchpads
        if device.device_type().is_touchpad() {
            device.set_natural_scroll(true);
        }
    });

    // There are no server-side decorations yet, so request all clients use client-side decorations.
    window::add_window_rule(|window| {
        window.set_decoration_mode(window::DecorationMode::ClientSide);
    });

    // Enable sloppy focus
    window::connect_signal(WindowSignal::PointerEnter(Box::new(|win| {
        win.set_focused(true);
    })));

    // Focus outputs when the pointer enters them
    output::connect_signal(OutputSignal::PointerEnter(Box::new(|output| {
        output.focus();
    })));
}