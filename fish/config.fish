set fish_greeting
if status is-interactive
    kotofetch --border false --centered false --horizontal-padding 1 --vertical-padding 1
end

source "$HOME/.cargo/env.fish"
zoxide init --cmd cd fish | source
