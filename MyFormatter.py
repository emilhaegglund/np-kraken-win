class MyFormatter(TickFormatter):
    """ Display ticks from a list of strings """
    labels = List(String)

    __implementation__ = """
        TickFormatter = require "models/formatters/tick_formatter"
        _ = require "underscore"
        Model = require "model"
        p = require "core/properties"
        class MyFormatter extends TickFormatter.Model
            type: "MyFormatter"



            doFormat: (ticks) ->
                labels = @labels
                return (labels[tick] ? "" for tick in ticks)


            @define {
                labels: [ p.Any ]
            }

        module.exports = 
            Model: MyFormatter
        """
