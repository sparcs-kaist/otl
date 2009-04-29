/*
 * Online Timeplanner with Lectures
 * 2009 Spring CS408 Capstone Project
 *
 * OTL Javascript Common Library
 * depends on: Mootools 1.2
 */

var Notifier = {
	initialize: function()
	{
		// Nothing to do.
	},
	showIndicator: function()
	{
		$('indicator').addClass('waiting');
	},
	setLoadingMsg: function(msg)
	{
		if (this.timeout)
			window.clearTimeout(this.timeout);
		$('indicator').addClass('waiting');
		$('message').set('html', msg);
		$('message-wrap').fade('show');
	},
	setMsg: function(msg)
	{
		this.clearIndicator();
		$('message').set('html', msg);
		$('message-wrap').fade('show');
		$('message-wrap').highlight('#FAD163');
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.timeout = window.setTimeout(function() {
			$('message-wrap').fade('out');
		}, 10000);
	},
	setErrorMsg: function(msg)
	{
		this.clearIndicator();
		$('message').set('html', msg);
		$('message-wrap').fade('show');
		$('message-wrap').highlight('#E55');
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.timeout = window.setTimeout(function() {
			$('message-wrap').fade('out');
		}, 10000);
	},
	clearIndicator: function()
	{
		$('indicator').removeClass('waiting');
	},
	clear: function()
	{
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.clearIndicator();
		$('message-wrap').fade('hide');
	}
}

var Map = {
	initialize:function()
	{
		this.container = $('map-drag-container');
		this.dragmap = $('dragmap');
		this.maptext= $('map-text');
		this.settings = 
		{
			cW:this.container.offsetWidth,
			cH:this.container.offsetHeight,
			dW:this.dragmap.offsetWidth,
			dH:this.dragmap.offsetHeight
		}

		this.dragging = false;
		this.clickPos = null

		this.dragmap.setStyle('left',-258);
		this.dragmap.setStyle('top',-270);
		this.registHandles();
	},
	registHandles:function()
	{
		this.fx = new Fx.Morph(this.dragmap, {
			wait:false,
			duration:250,
			transition: Fx.Transitions.Quad.easeInOut
			});

		this.dragHandler = this.onDrag.bindWithEvent(this);
		this.dragEndHandler = this.onEnd.bindWithEvent(this);
		this.dragmap.addEvent('mousedown',this.onMousedown.bindWithEvent(this));
	},
	onMousedown:function(e)
	{
		this.dragging=true;
		document.addEvent('mousemove', this.dragHandler);
		document.addEvent('mouseup', this.dragEndHandler);
		this.clickPos = UDF.mousePos(e,this.dragmap);
		e.stop();
	},
	onDrag:function(e)
	{
		if (this.dragging)
		{
			var pos = UDF.mousePos(e,this.container);
			pos.x-=this.clickPos.x;
			pos.y-=this.clickPos.y;

			var s = this.settings;
			var left = (pos.x).limit((s.cW-s.dW+2), 0);
			var top = (pos.y).limit((s.cH-s.dH+2), 0);
			this.dragmap.style.left=left+'px';
			this.dragmap.style.top=top+'px';
			this.previous_target = null;

			e.stop();
		}
	},
	onEnd:function(e)
	{
		document.removeEvent('mousemove', this.dragHandler);
		document.removeEvent('mouseup', this.dragEndHandler);
		if (this.dragging)
		{
			this.dragging=false;
			e.stop();
		}
	},
	move:function(x,y)
	{
		var s = this.settings;

		x-=(s.cW/2);
		y-=(s.cH/2);

		var left = (x).limit(0, s.dW-s.cW);
		var top = (y).limit(0, s.dH-s.cH);
		this.fx.start({
				left : (-left),
				top :(-top)
			});
	},
	find:function(name)
	{
		var arr = Data.Map.filter(function(item)
		{
			return item.name==name;
		});
		if (arr.length==0) return;

		var item = arr[0];
		var x = item.x;
		var y = item.y;
		this.maptext.style.left=(x-6)+'px';
		this.maptext.style.top=(y-60)+'px';
		$('map-name').innerHTML=item.code+' '+item.name;
		if (this.previous_target != item.name)
			this.move(x,y);
		this.previous_target = item.name;
	}
};
