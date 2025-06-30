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
use pinnacle_api::output::OutputHandle;
use pinnacle_api::pinnacle;
use pinnacle_api::pinnacle::Backend;
use pinnacle_api::process::Command;
use pinnacle_api::signal::OutputSignal;
use pinnacle_api::signal::WindowSignal;
use pinnacle_api::tag;
use pinnacle_api::tag::TagHandle;
use pinnacle_api::util::{Axis, Batch, Direction};
use pinnacle_api::window;

pub async fn keybinds(mod_key: Mod) {
    //------------------------
    // Mousebinds            |
    //------------------------

    // `mod_key + left click` starts moving a window
    input::mousebind(mod_key, MouseButton::Left)
        .on_press(|| {
            window::begin_move(MouseButton::Left);
        })
        .group("Mouse")
        .description("Start an interactive window move");

    // `mod_key + right click` starts resizing a window
    input::mousebind(mod_key, MouseButton::Right)
        .on_press(|| {
            window::begin_resize(MouseButton::Right);
        })
        .group("Mouse")
        .description("Start an interactive window resize");

    //------------------------
    // Keybinds              |
    //------------------------

    // `mod_key + s` shows the bindings overlay
    #[cfg(feature = "snowcap")]
    input::keybind(mod_key, 's')
        .on_press(|| {
            pinnacle_api::snowcap::BindOverlay::new().show();
        })
        .group("Compositor")
        .description("Show the bindings overlay");

    // `mod_key + shift + q` quits Pinnacle
    #[cfg(not(feature = "snowcap"))]
    input::keybind(mod_key | Mod::SHIFT, 'q')
        .set_as_quit()
        .group("Compositor")
        .description("Quit Pinnacle");

    #[cfg(feature = "snowcap")]
    {
        // `mod_key + shift + q` shows the quit prompt
        input::keybind(mod_key | Mod::SHIFT, 'q')
            .on_press(|| {
                pinnacle_api::snowcap::QuitPrompt::new().show();
            })
            .group("Compositor")
            .description("Show quit prompt");

        // `mod_key + ctrl + shift + q` for the hard shutdown
        input::keybind(mod_key | Mod::CTRL | Mod::SHIFT, 'q')
            .set_as_quit()
            .group("Compositor")
            .description("Quit Pinnacle without prompt");
    }

    // `mod_key + ctrl + r` reloads the config
    input::keybind(mod_key | Mod::CTRL, 'r')
        .set_as_reload_config()
        .group("Compositor")
        .description("Reload the config");

    // `mod_key + shift + c` closes the focused window
    input::keybind(mod_key | Mod::SHIFT, Keysym::Escape)
        .on_press(|| {
            if let Some(window) = window::get_focused() {
                window.close();
            }
        })
        .group("Window")
        .description("Close the focused window");

    // `mod_key + Return` spawns a terminal
    input::keybind(mod_key, Keysym::Return)
        .on_press(move || {
            Command::new(super::TERMINAL).spawn();
        })
        .group("Process")
        .description("Spawn a terminal");

    // `mod_key + q` spawns rofi
    input::keybind(mod_key, 'q')
        .on_press(move || {
            Command::new("wofi").args(["--show", "drun"]).spawn();
        })
        .group("Process")
        .description("Opens wofi menu");

    // `mod_key + space` toggles floating
    input::keybind(mod_key, Keysym::space)
        .on_press(|| {
            if let Some(window) = window::get_focused() {
                window.toggle_floating();
                window.raise();
            }
        })
        .group("Window")
        .description("Toggle floating on the focused window");

    // `mod_key + f` toggles fullscreen
    input::keybind(mod_key, 'f')
        .on_press(|| {
            if let Some(window) = window::get_focused() {
                window.toggle_fullscreen();
                window.raise();
            }
        })
        .group("Window")
        .description("Toggle fullscreen on the focused window");

    // `mod_key + m` toggles maximized
    input::keybind(mod_key, 'm')
        .on_press(|| {
            if let Some(window) = window::get_focused() {
                window.toggle_maximized();
                window.raise();
            }
        })
        .group("Window")
        .description("Toggle maximized on the focused window");
    
    // Directional operations
    let direction_map = [
        (Keysym::Up, Direction::Up, "above"),
        (Keysym::Down, Direction::Down, "below"),
        (Keysym::Left, Direction::Left, "left"),
        (Keysym::Right, Direction::Right, "right")
    ];
    for (key, direction, direction_name) in direction_map {

        // Focus direction
        input::keybind(mod_key, key)
            .on_press(move || {
                if let Some(current_focus_window) = window::get_focused() {
                    // Focus window
                    if let Some(new_focus_window) = current_focus_window.in_direction(direction).next() {
                        new_focus_window.set_focused(true);
                    }
                    // Focus output
                    else if let Some(new_focus_output) = output::get_focused().and_then(|o| o.in_direction(direction).next()) {
                        new_focus_output.focus();
                    }
                } else if let Some(new_focus_output) = output::get_focused().and_then(|o| o.in_direction(direction).next()) {
                    new_focus_output.focus();
                }
            })
            .group("Window")
            .description(format!("Focus {} window", direction_name));

        // Move window to direction
        input::keybind(mod_key | Mod::SHIFT, key)
            .on_press(move || {
                if let Some(current_focus_window) = window::get_focused() {
                    // Check if window on this side
                    //if let Some(new_focus_window) = current_focus_window.in_direction(direction).next() {
                    //    // Swap the two windowses
                    //}
                    
                    // Check if output in this direction
                    if let Some(new_focus_output) = output::get_focused().and_then(|o| o.in_direction(direction).next()) {
                        // Move to output
                        if let Some(tag) = new_focus_output.tags().next() {
                            current_focus_window.move_to_tag(&tag);
                            new_focus_output.focus();
                            tag.switch_to();
                        }
                    }
                }
            })
            .group("Window")
            .description(format!("Move focused window {} window", direction_name));
    }
    
    input::keybind(mod_key, Keysym::Tab)
        .on_press(|| {
            if let Some(tags) = output::get_focused().and_then(|o| Some(o.tags().collect::<Vec<TagHandle>>())) {
                let mut found_active = false;
                for tag in &tags {
                    if tag.active() {
                        found_active = true;
                    } else if found_active && tag.windows().next().is_some() {
                        tag.switch_to();
                        return;
                    }
                }
                
                if let Some(tag) = tags.iter().filter(|t| t.windows().next().is_some()).next() {
                    tag.switch_to();
                }
            };
        })
        .group("Window")
        .description("Switch to next tag");
}