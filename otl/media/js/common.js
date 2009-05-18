/*
 * Online Timeplanner with Lectures
 * 2009 Spring CS408 Capstone Project
 *
 * OTL Javascript Common Library
 * depends on: Mootools 1.2
 */

var Notifier = {
	/*
	 * Requires at least 3 elements in this structure:
	 * <div id="indicator"></div>
	 * <div id="message-wrap">
	 *   <div id="message"></div>
	 * </div>
	 */
	initialize: function(options)
	{
		var my_options = {
			indicator: $('indicator'),
			message: $('message'),
			wrapper: $('message-wrap'),
			clear_timeout: 10000,
		};
		$extend(my_options, options);
		this.indicator = my_options.indicator;
		this.message = my_options.message;
		this.wrapper = my_options.wrapper;
		this.clear_timeout = my_options.clear_timeout;
	},
	showIndicator: function()
	{
		this.indicator.addClass('waiting');
	},
	setLoadingMsg: function(msg)
	{
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.indicator.addClass('waiting');
		this.message.set('html', msg);
		this.wrapper.fade('show');
	},
	setMsg: function(msg)
	{
		this.clearIndicator();
		this.message.set('html', msg);
		this.wrapper.fade('show');
		this.wrapper.highlight('#FAD163');
		if (this.timeout)
			window.clearTimeout(this.timeout);
		if (this.clear_timeout > 0)
			this.timeout = window.setTimeout(function() {
				this.wrapper.fade('out');
			}, this.clear_timeout);
	},
	setErrorMsg: function(msg)
	{
		this.clearIndicator();
		this.message.set('html', msg);
		this.wrapper.fade('show');
		this.wrapper.highlight('#E55');
		if (this.timeout)
			window.clearTimeout(this.timeout);
		if (this.clear_timeout > 0)
			this.timeout = window.setTimeout(function() {
				this.wrapper.fade('out');
			}, this.clear_timeout);
	},
	clearIndicator: function()
	{
		this.indicator.removeClass('waiting');
	},
	clear: function()
	{
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.clearIndicator();
		this.wrapper.fade('hide');
	}
};

