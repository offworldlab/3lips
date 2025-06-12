" Octo PR Review Workflow Commands
" Save this as reference or source it in Neovim

" 1. Start reviewing PR #24
:Octo pr checkout 24
:Octo review start

" 2. Navigate between changed files
:Octo pr changes                " See all changed files
]c                              " Next change
[c                              " Previous change

" 3. Add comments while reviewing
:Octo review comment            " Comment on current line
" Type your comment and save (:wq)

" 4. Add code suggestions
:Octo review suggestions
" Format:
" ```suggestion
" your suggested code here
" ```

" 5. When done reviewing
:Octo review submit
" Choose: approve, comment, or request_changes

" Other useful commands during review:
:Octo pr ready                  " Mark PR as ready for review
:Octo pr checks                 " View CI status
:Octo pr reload                 " Reload PR data
:Octo pr merge                  " Merge when approved

" View existing reviews
:Octo pr reviews

" Jump to specific parts
:Octo pr jump_to_file          " Interactive file picker
:Octo comment next             " Next comment
:Octo comment prev             " Previous comment