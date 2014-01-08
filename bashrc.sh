# Dev is a wrapper, so add completions.
# `dev [-u <user>] [<command> [<args>]]`
function _dev_completions {
    
    local cword pword
    cword="${COMP_WORDS[COMP_CWORD]}"
    pword="${COMP_WORDS[$((COMP_CWORD - 1))]}"
    
    case "$pword" in
    
        -u | --user )
            COMPREPLY=( $(compgen -u -- "$cword") )
            ;;
        
    esac
}
complete -cf -F _dev_completions dev


function dev-shell {
    # Save all of the KS variables so that we can restore them.
    export _OLD_KS_ENV="$(env | grep '^KS_')"
    eval "$(dev --export "$@")"
}

function dev-deactivate {
    if [[ -n "$_OLD_KS_ENV" ]]; then

        # Wipe out the current KS variables.
        local name
        for name in $(env | grep '^KS_' | cut -d= -f1); do
            unset $name
        done

        # Restore!
        eval "$_OLD_KS_ENV"
        unset _OLD_KS_ENV

    fi
}

