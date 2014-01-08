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
    eval "$(dev --export "$@")"
}

