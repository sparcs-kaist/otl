"use strict";
/*
 * Online Timeplanner with Lectures
 * 2009 Spring CS408 Capstone Project
 *
 * OTL Timetable Javascript Implementation
 * depends on: jQuery 1.4.2, OTL Javascript Common Library
 */

/* Example of a lecture item.
Data.Lectures = 
[
	{
		id:'1',
		dept_id:'3847',
		classification:'기초필수',
		course_no:'CS202',
		class_no:'A',
		code:'37.231',
		title:'데이타구조',
		lec_time:'2',
		lab_time:'3',
		credit:'3',
		prof:'김민우',
		times:[{day:'화',start:480,end:600},{day:'수',start:480,end:600}],
		classroom:'창의학습관 304',
		limit:'200',
		num_people:'47',
		remarks:'영어강의',
		examtime:{day:'화,start:480,end:630}
	}
];
*/
function roundD(n, digits) {
	if (digits >= 0) return parseFloat(n.toFixed(digits));
	digits = Math.pow(10, digits);
	var t = Math.round(n * digits) / digits;
	return parseFloat(t.toFixed(0));
}

var NUM_ITEMS_PER_LIST = 15;
var NUM_ITEMS_PER_DICT_COMMENT = 10;
var NUM_ITEMS_PER_INDEX_COMMENT = 15;
var NUMBER_OF_TABS = 3;
var Data = {};
var Mootabs = function(tabContainer, contents, trigerEvent, useAsTimetable)
	{
		if (trigerEvent==undefined) trigerEvent = 'mouseover';
		this.data = [];
		this.is_timetable = useAsTimetable ? true : false;

		this.tabs = $(tabContainer).children();
		this.contents = $(contents).children();
		$.each(this.tabs, $.proxy(function(index, item) {
			if (this.is_timetable)
				Data.Timetables[index] = {credit:0, au:0};
			$(item).bind(trigerEvent, $.proxy(function() {
				this.activate(index);
			}, this));
		}, this));
		$.each(this.contents, function(index, item)
		{
			$(item).addClass('none');
		});
		this.activate(0);
	};
Mootabs.prototype.setData = function(index,data)
	{
		this.data[index] = data;
	};
Mootabs.prototype.activate = function(key)
	{
		$.each(this.tabs, function(index, item)
		{
			if (index==key)
				$(item).addClass('active');
			else
				$(item).removeClass('active');
		});
		$.each(this.contents, function(index, item)
		{
			if (index==key) $(item).removeClass('none');
			else $(item).addClass('none');
		});
		this.activeKey = key;
	};
Mootabs.prototype.getTableId = function()
	{
		return this.activeKey;
	};

var Utils = {
	modulecolors:
		['#FFC7FE','#FFCECE','#DFE8F3','#D1E9FF','#D2F1EE','#FFEAD1','#E1D1FF','#FAFFC1','#D4FFC1','#DEDEDE','#BDBDBD'],
	modulecolors_highlighted:
		['#feb1fd','#ffb5b5','#c9dcf2','#b7dbfd','#b5f1eb','#fbd8ae','#d4bdfd','#f1f89f','#b9f2a0','#cbc7c7','#aca6a6'],
	getColorByIndex: function(index)
	{
		//index =index*3;
		//index = Utils.modulecolors.length % index;
		return index % Utils.modulecolors.length;
	},
	mousePos: function(ev, wrap)
	{
		return {
			x: ev.pageX - $(wrap).offset().left,
			y: ev.pageY - $(wrap).offset().top
		};
	},
	clickable: function(o)
	{
		$(o).bind('mousedown',function(){ $(o).addClass('clicked') });
	},
	NumericTimeToReadable: function(t)
	{
		var hour = Math.floor(t / 60);
		var minute = t % 60;
		return (hour < 10 ? '0':'') + hour + ':' + (minute < 10 ? '0':'') + minute;
	}
};

var CourseList = {
	initialize:function(tabs,contents)
	{
		this.tabs = $('#lecture_tabs');
		this.contents = $('#lecture_contents');
		this.data = Data.Lectures;
		this.dept = $('#department');
		this.classf = $('#classification');
		this.keyword = $('#keyword');
		this.apply = $('#apply');
		this.in_category = $('#in_category');

		this.loading = true;
		this.dept.selectedIndex = 0;
		this.registerHandles();
		this.getAutocompleteList();
		this.onChange();
	},
	registerHandles:function()
	{
		$(this.dept).bind('change', $.proxy(this.onClassChange, this));
		$(this.classf).bind('change', $.proxy(this.onClassChange, this));
		$(this.apply).bind('click', $.proxy(this.onChange, this));
		$(this.in_category).bind('change', $.proxy(this.onInCategoryChange, this));
		$(this.keyword).bind('keypress', $.proxy(function(e) { if(e.keyCode == 13) { this.onChange(); }}, this));
	},
	getAutocompleteList:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		var in_category = $(this.in_category).is(':checked');
		var conditions = {};
		if( in_category )
			conditions = {'year': Data.ViewYear, 'term': Data.ViewTerm, 'dept': dept, 'type': classification, 'lang': USER_LANGUAGE};
		else
			conditions = {'year': Data.ViewYear, 'term': Data.ViewTerm, 'dept': -1, 'type': '전체보기', 'lang': USER_LANGUAGE};
		$.ajax({
			type: 'GET',
			url: '/dictionary/autocomplete/',
			data: conditions,
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					this.keyword.flushCache();
					this.keyword.autocomplete(resObj, {
						matchContains: true,
						scroll: true,
						width: 197,
						selectFirst: false
					});
				} catch(e) {
				}
			}, this),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
			}, this)
		});
	},
	onInCategoryChange:function()
	{
		this.getAutocompleteList();
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		if( keyword != '' )
			this.onChange();
	},
	onClassChange:function()
	{
		var in_category = $(this.in_category).is(':checked');
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		if( in_category )
			this.getAutocompleteList();
		if( in_category || keyword == '')
			this.onChange();
	},
	onChange:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		var in_category = $(this.in_category).is(':checked');
		//TODO: classification을 언어와 상관 없도록 고쳐야 함
		if (dept == '-1' && USER_LANGUAGE == 'ko' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('키워드 없이 학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else if (dept == '-1' && USER_LANGUAGE == 'en' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('You must select a course type if you want to see \'ALL\' departments without keywords.');
		else {
			if( in_category || keyword == '')
				this.filter({'dept':dept,'type':classification,'lang':USER_LANGUAGE,'keyword':keyword});
			else
				this.filter({'dept':-1,'type':'전체보기','lang':USER_LANGUAGE,'keyword':keyword});
		}
	},
	clearList:function()
	{
		CourseList.contents.empty(); 
		CourseList.buildTabs(CourseList.contents.children().length);
	},
	addToListMultiple:function(obj)
	{
		CourseList.contents.empty(); 
		var max = NUM_ITEMS_PER_LIST;
		var count=0;
		var content = $('<div>', {'class': 'lecture_content'});
		content.appendTo(CourseList.contents);
		var currCategory;
		$.each(obj, function(index, item) {
			var key = item.classification;
			if (currCategory != key) {
				currCategory = key;
				if (count < max) $('<h4>').text(currCategory).appendTo(content);
			}

			if (count>=max) {
				content = $('<div>', {'class':'lecture_content'}).appendTo(CourseList.contents);
				$('<h4>').text(currCategory).appendTo(content);
				count=0;
			} else
				count++;

			var el = $('<a>').text(item.title).appendTo(content);
			Utils.clickable(el);

			el.bind('mousedown', $.proxyWithArgs(CourseList.seeCourseComments, CourseList, item));
		});
		CourseList.buildTabs(CourseList.contents.children().length);
		new Mootabs($('#lecture_tabs'), $('#lecture_contents'));
	},
	filter:function(conditions)
	{
		//TODO: conditions.type와 상관 없도록 고쳐야 함
		if (conditions.type == undefined){
			conditions.type = '전체보기';
		}
		$.ajax({
			type: 'GET',
			url: '/dictionary/search/',
			data: conditions,
			dataType: 'json',
			beforeSend: $.proxy(function() {
				if (this.loading)
					Notifier.showIndicator();
				else
					Notifier.setLoadingMsg(gettext('검색 중입니다...'));
			}, this),
			success: $.proxy(function(resObj) {
				try {
					if (resObj.length == 0) {
						CourseList.clearList();
						if (!this.loading)
							Notifier.setErrorMsg(gettext('과목 정보를 찾지 못했습니다.'));
					} else {
						CourseList.addToListMultiple(resObj);
						if (!this.loading)
							Notifier.setMsg(gettext('검색 결과를 확인하세요.'));
					}
				} catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
				if (this.loading)
					Notifier.clearIndicator();
				this.loading = false;
			}, this),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
				Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				this.loading = false;
			}, this)
		});
	},
	buildTabs:function(n)
	{
		this.tabs.empty();
		for (var i=1;i<=n;i++) {
			var tab = $('<div>',{'class':'lecture_tab'});
			$('<div>').text(i).appendTo(tab);
			tab.appendTo(this.tabs);
		}
	},
	seeCourseComments:function(e,obj)
	{
		var course_no = obj.course_no;
		var url = '/dictionary/view/' + course_no + '/';
		$.post(url, function(data) {
			window.location = url;
		});
		/*
		$.ajax({
				type: 'GET', 
				url: '/dictionary/view/'+course_no,
				data: {'course_no':course_no},
				dataType: 'json',
				success: $.proxy(function(resObj)
				{
					try {
						if (resObj.result=='OK') {
						} else {
							var msg;
							Notifier.setErrorMsg(msg);
						}
					}
					catch(e) {
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
					}
				}, this),
				error: function(xhr) {
					if (suppress_ajax_errors)
						return;
					if (xhr.status == 403){
						Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
					}
					else{
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
					}
				}
			});
		*/
	}
};

var DictionaryCommentList = {
	initialize:function()
	{
		this.comments = $('#course-comment-view');
		this.submitComment = $('input[name="submitComment"]');
		this.onLoad();
		this.registerHandles();
	},
	onLoad:function()
	{
		this.addToMultipleComment(Data.DictionaryComment);
	},
	registerHandles:function()
	{
		$(this.submitComment).bind('mousedown', $.proxy(this.addComment, this));
	},
	addComment:function()
	{
		var new_comment_content = $('textarea[name="comment"]').val();
		var new_comment_load = $('input[name="load"]:checked').val();
		var new_comment_score = $('input[name="score"]:checked').val();
		var new_comment_gain = $('input[name="gain"]:checked').val();
		var course_id = Data.Course.id;
		var lecture_id = Data.current_lecture_id;

		if (!new_comment_load || !new_comment_score || !new_comment_gain) {
			Notifier.setErrorMsg(gettext('로드, 학점, 남는거를 선택하세요.'));
		}
		else {
			$.ajax({
				type: 'POST', 
				url: '/dictionary/add_comment/',
				data: {'comment': new_comment_content, 'load': new_comment_load, 'score': new_comment_score, 'gain': new_comment_gain, 'lecture_id': lecture_id, 'course_id': course_id},
				dataType: 'json',
				success: $.proxy(function(resObj) {
					try {
						if (resObj.result=='ADD') {
							DictionaryCommentList.update(resObj.comment)							
							DictionaryCommentList.addToMultipleComment(resObj.comment)
						} else if (resObj.result='ALREADY_WRITTEN') {
							Notifier.setErrorMsg(gettext('이미 등록하셨습니다.'));
						}
					}
					catch(e) {
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
					}
				}, this),
				error: function(xhr) {
					if (suppress_ajax_errors)
						return;
					if (xhr.status == 403){
						Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
					}
					else{
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
					}
				}
			});
		}
	},
	deleteComment:function(e,obj) 
	{
		$.ajax({
			type: 'POST',
			url: '/dictionary/delete_comment/',
			data: {'comment_id': obj.comment_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='DELETE') {
						DictionaryCommentList.update(resObj.comment);
						DictionaryCommentList.addToMultipleComment(resObj.comment);
					} else if (resObj=='REMOVE_NOT_EXIST') {
						Notifier.setErrorMsg(gettext('잘못된 접근입니다.'));
					}
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if (xhr.status == 403) {
					Notifier.setErrorMsg(gettext('로그인 해야합니다.'));
				}	
				else {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},
	addToMultipleComment:function(obj)
	{
		var max = NUM_ITEMS_PER_DICT_COMMENT;
		var count=0;
		this.clearComment();
		$.each(obj, function(index, item) {
			var enableDelete = (item.writer_id == Data.user_id);
			var comment = $('<div>', {'class': 'dictionary_comment'});
			comment.appendTo(DictionaryCommentList.comments);

			$('<a>').text(item.writer_nickname).appendTo(comment);
			$('<div>', {'class': 'dictionary_comment_content'}).text(item.comment).appendTo(comment);
			//$('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("평가") + '-');
			//$('<span>').text(gettext("학점") + ':')
			//$('<span>').text(get</span>{{comment.load}}</span>, {% trans "학점" %} : <span>{{comment.score}}</span>, {% trans "남는거" %} : <span>{{comment.gain}}</span>, By {{comment.writer}} ({{comment.written_datetime|date:"Y/m/d"}}').appendTo(comment);
			
			if (enableDelete) {
				var deletelink = $('<div>', {'class': 'dictionary_comment_delete'}).text("지우기").appendTo(comment);
				deletelink.bind('click', $.proxyWithArgs(DictionaryCommentList.deleteComment, DictionaryCommentList, item));
			}
		});

	},
	clearComment:function()
	{
		this.comments.empty();
	},
	update:function(obj)
	{
		Data.DictionaryComment = {};
		$.each(obj, function(index, item) {
			Data.DictionaryComment[item.comment_id] = item;
		});
	}
};

var IndexCommentList = {
	initialize:function() 
	{
		this.comments = Data.Comments;	
		this.timeline = $('#timeline');
		this.registerHandles();
		this.updateComment();
	},
	registerHandles:function()
	{
	},
	updateComment:function()
	{
		var max = NUM_ITEMS_PER_INDEX_COMMENT;
		$.ajax ({
			type: 'POST',
			url: '/dictionary/update_comment/',
			data: {'count': max},
			dataType: 'json',
			success: function (resObj) {
				try {
					if (resObj.result=='OK') {
						IndexCommentList.addToMultipleComment(resObj.comments)
					}
					else {
						Notifier.setErrrorMsg(gettext('오류가 발생했습니다.'));
					}
				} catch (e) {
					Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
				}	
			},
			error: function (xhr) {
				Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
			}	   
		});
	},
	addToMultipleComment:function(obj)
	{
		$.each(obj, function(index, item) {
			var div_comment = $('<div>', {'class': 'timeline_comment'});
			div_comment.appendTo(IndexCommentList.timeline);

			var left_div_comment = $('<div>', {'class': 'timeline_comment_left'});
			var right_div_comment = $('<div>', {'class': 'timeline_comment_right'});

			left_div_comment.appendTo(div_comment);
			right_div_comment.appendTo(div_comment);

			$('<a>', {'class': 'content_prof_photo'}).text('사진').appendTo(left_div_comment);
			$('<a>', {'class': 'content_prof_name'}).text(item.professor[0].professor_name).appendTo(left_div_comment);

			var top_right_div_comment = $('<div>', {'class': 'timeline_comment_right_subject'});
			var mid_right_div_comment = $('<div>', {'class': 'timeline_comment_right_comment'});
			var down_right_div_comment = $('<div>', {'class': 'timeline_comemnt_right_eval'});

			top_right_div_comment.appendTo(right_div_comment);
			mid_right_div_comment.appendTo(right_div_comment);
			down_right_div_comment.appendTo(right_div_comment);

			$('<a>', {'class': 'content_subject'}).text(item.course_title).appendTo(top_right_div_comment);
			$('<a>', {'class': 'content_comment'}).text(item.comment).appendTo(mid_right_div_comment);
			$('<a>', {'class': 'content_score'}).text('학점 :' + item.score).appendTo(down_right_div_comment);
			$('<a>', {'class': 'content_load'}).text('로드 :' + item.load).appendTo(down_right_div_comment);
			$('<a>', {'class': 'content_gain'}).text('남는거 :' + item.gain).appendTo(down_right_div_comment);
		});
	}
};	
