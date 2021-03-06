fn maxjob_backend_on_tick s e = (
    /***Must be global for the timer to find it.***/
    flushLog()

    -- FIXME
    -- For some reason the flush does not reliably update the logfile.
    -- Closing and reopening it does, but is probably too heavy.
    if ::maxjob_backend != undefined do (
        local logfile = ::maxjob_backend.logfile
        if doesFileExist logfile do (
            closeLog()
            openLog logfile mode:"a"
        )
    )
)


struct maxjob_backend (
    /***Implement functionality for polling maxscript log changes.***/

    _flushtimer,
    _interval = 1000,  -- Milliseconds.

    logfile = (systemTools.getEnvVariable "MAXJOB_BACKEND_LOGFILE") as string,

    _csharpcode = "
        using System;

        class StdOutPrinter {
            static public bool print(string txt) {
                Console.WriteLine(txt);
                return true;
            }
        }

        class StdErrPrinter {
            static public bool print(string txt) {
                Console.Error.WriteLine(txt);
                return true;
            }
        }
    ",

    fn _init_channels = (
        fn _create_assembly code className = (
            local provider = dotNetObject "Microsoft.CSharp.CSharpCodeProvider"
            local param = dotNetObject "System.CodeDom.Compiler.CompilerParameters"
            param.GenerateInMemory = on
            local compiled = provider.CompileAssemblyFromSource param #(this._csharpcode)
            compiled.CompiledAssembly.CreateInstance className
        )

        global stdout = _create_assembly code "StdOutPrinter"
        global stderr = _create_assembly code "StdErrPrinter"
    ),

    fn _init_logfile = (
        deleteFile this.logfile
        openLog this.logfile
    ),

    fn _init_flush_timer = (
        if this._flushtimer != undefined do
            try(this._flushtimer.Stop())catch()

        this._flushtimer = dotNetObject "System.Timers.Timer"
        this._flushtimer.Interval = this._interval

        dotNet.addEventHandler this._flushtimer "Elapsed" maxjob_backend_on_tick
        this._flushtimer.Start()
        true
    ),

    fn init = (
        this._init_channels()
        this._init_logfile()
        this._init_flush_timer()
        ::stdout.print "maxjob_backend initialized."
    )
)

global maxjob_backend = maxjob_backend()
maxjob_backend.init()
