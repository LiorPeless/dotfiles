let mapleader = "\<Space>"
let g:NERDTreeWinPos = "right"
let g:python_highlight_all = 1 " set python syntax highlighting on
" For LSP
let g:lsp_log_verbose = 1
let g:lsp_log_file = expand('~/vim-lsp.log')

" configure airline
let g:airline#extensions#tabline#enabled = 1 " set a tab line at top
let g:airline_theme='base16' " set color for aairline

let base16_colorspace=256 " Access colors present in 256 colorspace


" enable clipboard
set clipboard=unnamed

" configure fzf
let g:fzf_layout = { 'window': { 'width': 0.9, 'height': 0.9 } }
" let g:fzf_preview_window = ['right:50%', 'ctrl-/']

syntax on

set number
set relativenumber
set complete+=kspell
set completeopt=menuone,longest
" set laststatus=2


" default updatetime 4000ms is not good for async update
set updatetime=100


" " my youtube music player - runs from a binary inside the vim directory
" command Music call OpenTerminalAndRunMusic()
" function! OpenTerminalAndRunMusic()
"     " Open a new terminal buffer
"     above terminal ++cols=40 ++rows=2
"     " Send the command to run the executable files
"     call term_sendkeys(bufnr("$"), "python C:\\tools\\vim\\music_player\\main_curses.py\<CR>")
"     " call term_sendkeys(bufnr("$"), "music_player\\main_curses.py\<CR>")
" endfunction


" color scheme:
" set background=dark
" colorscheme retrobox

autocmd VimEnter * :color abstract
autocmd VimEnter * :color default
"autocmd VimEnter * :color molokai
autocmd VimEnter * :AirlineTheme molokai
autocmd VimEnter * :set belloff=all


set tabstop=4
set shiftwidth=4
set expandtab

nnoremap <leader>e :NERDTreeToggle<CR>
nnoremap <leader>f :FZF<CR>
" git commands
nnoremap <leader>gb :Git blame<CR>
nnoremap <leader>gs :Git<CR>
nnoremap <leader>ff :Autoformat<CR>

" IMPORTANT: make sure to set this to where your plugins folder is located
call plug#begin('$HOME/vimfiles/plugged')
    
    " For LSP
	Plug 'prabirshrestha/vim-lsp'
	Plug 'mattn/vim-lsp-settings'
	" For Auto Completion + using AI
    Plug 'vim-scripts/AutoComplPop'
	Plug 'Exafunction/codeium.vim'
    " For files tree
	Plug 'preservim/nerdtree'
    " For fuzzy search
	Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
    " for python stntax highlight
    Plug 'vim-python/python-syntax'
    " for git
    Plug 'tpope/vim-fugitive'
    Plug 'mhinz/vim-signify', { 'tag': 'legacy' }
    " for statusline
    Plug 'vim-airline/vim-airline'
    Plug 'vim-airline/vim-airline-themes'
    " for color scheme
    Plug 'rafi/awesome-vim-colorschemes'
    " for python formatting
    Plug 'vim-autoformat/vim-autoformat'

call plug#end()


function! s:on_lsp_buffer_enabled() abort
	setlocal omnifunc=lsp#complete
endfunction


augroup lsp_install
	au!
	autocmd User lsp_buffer_enabled call s:on_lsp_buffer_enabled()
augroup END
