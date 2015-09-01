fn maxjob_backend_on_tick s e = (
    /***Must be global for the timer to find it.***/
    flushLog()
)


struct maxjob_backend (

    _flushtimer,
    _interval = 1000,  -- Milliseconds.

    logfile = @"C:\Users\Buelter\Desktop\maxjob.log",

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

    fn init_channels = (
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

    fn init_logfile = (
        openLog this.logfile
    ),

    fn init_flush_timer = (
        if this._flushtimer != undefined do
            try(this._flushtimer.Stop())catch()

        this._flushtimer = dotNetObject "System.Timers.Timer"
        this._flushtimer.Interval = this._interval

        dotNet.addEventHandler this._flushtimer "Elapsed" maxjob_backend_on_tick
        this._flushtimer.Start()
        true
    )
)

global maxjob_backend = maxjob_backend()

maxjob_backend.init_channels()
maxjob_backend.init_logfile()
maxjob_backend.init_flush_timer()

-- do stuff to produce listener output
filein @"C:\Users\Buelter\Google Drive\dev\mxs_types\mxs_types.ms"
teapot()
delete objects
a = mxs_set()
b = mxs_dict()
print renderers.current
print "foobar"
format "%\n" "noice job!!11"

::stdout.print "INFO - maxjob backend initiated."