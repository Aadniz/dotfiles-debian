set fish_greeting
if status is-interactive
    kotofetch --border false --centered false --horizontal-padding 1 --vertical-padding 1 --modes $HOME/.config/kotofetch/quotes/*
end

set --export ANDROID_HOME $HOME/Android/Sdk
set -gx PATH $ANDROID_HOME/emulator $PATH;
set -gx PATH $ANDROID_HOME/tools $PATH;
set -gx PATH $ANDROID_HOME/tools/bin $PATH;
set -gx PATH $ANDROID_HOME/platform-tools $PATH;

set --export JAVA_HOME /usr/lib/jvm/java-21-openjdk-amd64

source "$HOME/.cargo/env.fish"
zoxide init --cmd cd fish | source
