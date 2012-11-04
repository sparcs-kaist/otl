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
		type:'기초필수',
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
var NUM_ITEMS_PER_PROF_COMMENT = 15;
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
	},
	post_to_url:function(path, params, method) 
	{
		method = method || "post";
		var form = document.createElement("form");
		form.setAttribute("method", method);
		form.setAttribute("action", path);
		for (var key in params) {
			var hiddenField = document.createElement("input");
			hiddenField.setAttribute("type", "hidden");
			hiddenField.setAttribute("name", key);
			hiddenField.setAttribute("value", params[key]);
			form.appendChild(hiddenField);
		}
		document.body.appendChild(form);
		form.submit();
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
		if (this.pre_active_tab === -1) this.onChange();
		else this.onPreChange();
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
	onPreChange:function()
	{
		if (this.pre_keyword === false) this.pre_keyword = '';

		document.getElementById("department").selectedIndex = this.pre_dept;
		document.getElementById("classification").selectedIndex = this.pre_classification;
		document.getElementById("keyword").value = this.pre_keyword;
		document.getElementById("in_category").checked = this.pre_in_category;

		var dept = document.getElementById("department")[this.pre_dept].value;
		var classification = document.getElementById("classification")[this.pre_classification].value;
		var keyword = this.pre_keyword.replace(/^s+|\s+$/g, '');
		var in_category = this.pre_in_category;
		var active_tab = this.pre_active_tab-1;

		if (dept == '-1' && USER_LANGUAGE == 'ko' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('키워드 없이 학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else if (dept == '-1' && USER_LANGUAGE == 'en' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('You must select a course type if you want to see \'ALL\' departments without keywords.');
		else {
			if( in_category || keyword == '')
				this.filter({'dept':dept,'type':classification,'lang':USER_LANGUAGE,'keyword':keyword},active_tab);
			else
				this.filter({'dept':-1,'type':'전체보기','lang':USER_LANGUAGE,'keyword':keyword},active_tab);
		}
		this.pre_active_tab=-1;
	},
	clearList:function()
	{
		CourseList.contents.empty(); 
		CourseList.buildTabs(CourseList.contents.children().length);
	},
	addToListMultiple:function(obj,active_tab)
	{
		if (active_tab===undefined) active_tab=0;
		CourseList.contents.empty(); 
		var max = NUM_ITEMS_PER_LIST;
		var count=0;
                var flag=0;
		var content = $('<div>', {'class': 'lecture_content'});
		content.appendTo(CourseList.contents);
		var currCategory='교수정보';
                
		$.each(obj.professors, function(index, item) {
                        if(flag==0&&count==0) {
                            $('<h4>').text(currCategory).appendTo(content);
                            flag=1;
                        }
                        if(count>=max) {
				content = $('<div>', {'class':'lecture_content'}).appendTo(CourseList.contents);
				$('<h4>').text(currCategory).appendTo(content);
				count=0;
                        } else
                                count++;

			var el = $('<a>').text(item.professor_name).appendTo(content);
			Utils.clickable(el);

			el.bind('mousedown', $.proxyWithArgs(CourseList.seeProfessorInfo, CourseList, item));
                });
		$.each(obj.courses, function(index, item) {
			var key = item.type;
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
		this.mootabs = new Mootabs($('#lecture_tabs'), $('#lecture_contents'));
		this.mootabs.activate(active_tab);
	},
	filter:function(conditions,active_tab)
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
					if (resObj.courses.length == 0 && resObj.professors.length == 0) {
						CourseList.clearList();
						if (!this.loading)
							Notifier.setErrorMsg(gettext('과목 정보를 찾지 못했습니다.'));
					} else {
						CourseList.addToListMultiple(resObj,active_tab);
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
		var old_code = obj.old_code;
		var url = '/dictionary/view/' + old_code + '/';

		var dept = document.getElementById("department").selectedIndex;
		var classification = document.getElementById("classification").selectedIndex;
		var keyword = $(this.keyword).val();
		var in_category = $(this.in_category).is(':checked');
		var active_tab = $('div[class="lecture_tab active"]').text();
		var sendData = {'dept':dept, 'classification':classification, 'keyword':keyword, 'in_category':in_category, 'active_tab':active_tab};

		Utils.post_to_url(url, sendData, 'GET');
	},
	seeProfessorInfo:function(e,obj)
	{
		var professor_id = obj.professor_id;
		var url = '/dictionary/professor/' + professor_id + '/';

		var dept = document.getElementById("department").selectedIndex;
		var classification = document.getElementById("classification").selectedIndex;
		var keyword = $(this.keyword).val();
		var in_category = $(this.in_category).is(':checked');
		var active_tab = $('div[class="lecture_tab active"]').text();
		var sendData = {'dept':dept, 'classification':classification, 'keyword':keyword, 'in_category':in_category, 'active_tab':active_tab};

		Utils.post_to_url(url, sendData, 'GET');
	},
};

var DictionaryCommentList = {
	initialize:function()
	{
		this.summary = $('#course-summary');
		this.lecture_summary = $('#lecture-summary');
		this.comments = $('#course-comment-view');
		this.submitComment = $('input[name="submitComment"]');
		this.onLoad();
		this.registerHandles();
                this.loading=true;
	},
	onLoad:function()
	{
		this.addToMultipleProfessor(Data.Professors);
		this.onChangeProfessor(DictionaryCommentList, null);
	},
	registerHandles:function()
	{
		$(this.submitComment).bind('mousedown', $.proxy(this.addComment, this));
		$(this.addSummarySend).bind('mousedown', $.proxy(this.addSummary, this));

                $(window).scroll(function() {
                    if(!DictionaryCommentList.loading){
                    if($(window).scrollTop() + $(window).height() == $(document).height()) {
			    DictionaryCommentList.showMoreComments();

                    }
                    }
                });

	},

	showMoreComments:function()
	{
		if (Data.comment_id!=0){
			var conditions = {'course_id': Data.Course.id, 'next_comment_id': Data.comment_id, 'professor_id': Data.current_professor_id};
			$.ajax({
				type: 'GET',
				url: '/dictionary/show_more_comments/',
				data: conditions,
				dataType: 'json',
				success: $.proxy(function(resObj) {
					try {
						Data.comment_id = resObj.next_comment_id;
						DictionaryCommentList.addToMultipleComment(resObj.comments);
                                                Data.DictionaryComment = Data.DictionaryComment.concat(resObj.comments);
					} catch(e) {
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
					}
                                        this.loading = false;

				}, this),
				error: $.proxy(function(xhr) {
					if (suppress_ajax_errors)
						return;
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
                                        this.loading = false;
				}, this)
			});
		}

	},
	showSummary:function()
	{
		$('#course-explain').hide();
		$('#course-require').hide();
		$('#course-summary-add-img').hide();
		$('#course-explain-add').show();
		$('#course-require-add').show();
		$('#course-summary-complete-img').show();
	},
	showLectureSummary:function()
	{
		$('#lecture-homepage').hide();
		$('#lecture-mainbook').hide();
		$('#lecture-subbook').hide();
		$('#lecture-summary-add-img').hide();
		$('#lecture-homepage-add').show();
		$('#lecture-mainbook-add').show();
		$('#lecture-subbook-add').show();
		$('#lecture-summary-complete-img').show();
	},
	addSummary:function()
	{
		var new_explain_content = $("#course-explain-add").val();
		var new_require_content = $('#course-require-add').val();
		var course_id = Data.Course.id;
                var writer_id = Data.user_id;
                $.ajax({
                    type: 'POST',
                    url: '/dictionary/add_summary/',
  					data: {'content': new_explain_content, 'require': new_require_content, 'course_id': course_id, 'writer_id': writer_id},
                    dataType: 'json',
                    success: $.proxy(function(resObj) {
                        try {
                            if (resObj.result=='OK') {
                                Data.summary = resObj.summary
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
		var output_explain = new_explain_content.replace(/\n/g,'<br />');
		var output_require = new_require_content.replace(/\n/g,'<br />');
		$("#course-require").html(output_require);
		$("#course-explain").html(output_explain);
		$('#course-explain-add').hide();
		$('#course-require-add').hide();
		$('#course-summary-complete-img').hide();
		$('#course-explain').show();
		$('#course-require').show();
		$('#course-summary-add-img').show();
	},
	addLectureSummary:function()
	{
		var new_homepage_content = $("#lecture-homepage-add").val();
		var new_mainbook_content = $('#lecture-mainbook-add').val();
		var new_subbook_content = $('#lecture-subbook-add').val();
		var course_id = Data.Course.id;
		var prof_id = Data.current_professor_id;
                var writer_id = Data.user_id;
                $.ajax({
                    type: 'POST',
                    url: '/dictionary/add_lecture_summary/',
  					data: {'homepage': new_homepage_content, 'mainbook': new_mainbook_content, 'subbook': new_subbook_content, 'course_id': course_id, 'writer_id': writer_id, 'professor_id':prof_id},
                    dataType: 'json',
                    success: $.proxy(function(resObj) {
                        try {
                            if (resObj.result=='OK') {
                                Data.lecturesummary = resObj.summary
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
		var output_homepage = new_homepage_content.replace(/\n/g,'<br />');
		var output_mainbook = new_mainbook_content.replace(/\n/g,'<br />');
		var output_subbook = new_subbook_content.replace(/\n/g,'<br />');

		$('#lecture-homepage').html(output_homepage);
		$('#lecture-mainbook').html(output_mainbook);
		$('#lecture-subbook').html(output_subbook);
		$('#lecture-homepage-add').hide();
		$('#lecture-mainbook-add').hide();
		$('#lecture-subbook-add').hide();
		$('#lecture-summary-complete-img').hide();
		$('#lecture-homepage').show();
		$('#lecture-mainbook').show();
		$('#lecture-subbook').show();
		$('#lecture-summary-add-img').show();
	},

	addComment:function()
	{
		var new_comment_content = $('textarea[name="comment"]').val();
		var new_comment_load = $('input[name="load"]:checked').val();
		var new_comment_score = $('input[name="score"]:checked').val();
		var new_comment_gain = $('input[name="gain"]:checked').val();
		var course_id = Data.Course.id;
		var lecture_id = -1;

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
							DictionaryCommentList.addToFront(resObj.comment);							
							DictionaryCommentList.addNewComment(resObj.comment);
							$($("#course-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
							$($("#course-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
							$($("#course-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
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
	deleteComment:function(e,obj, comment) 
	{
		$.ajax({
			type: 'POST',
			url: '/dictionary/delete_comment/',
			data: {'comment_id': obj.comment_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='DELETE') {
                                            comment.remove();
                                            $($("#course-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
                                            $($("#course-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
                                            $($("#course-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
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
			
		$.each(obj, function(index, item) {
			var enableDelete = (item.writer_id == Data.user_id);
			var comment = $('<div>', {'class': 'dictionary_comment'});
			var comment_output = item.comment.replace(/\n/g,'<br />');
			comment.appendTo(DictionaryCommentList.comments);
	
			$('<a>').text(item.writer_nickname).appendTo(comment);
			$('<div>', {'class': 'dictionary_comment_content'}).html(comment_output).appendTo(comment);
			$('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("학점") + ':' + item.score).appendTo(comment);
			$('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("로드") + ':' + item.load).appendTo(comment);
			$('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("남는거") + ':' + item.gain).appendTo(comment);
		
			if (enableDelete) {
				var deletelink = $('<div>', {'class': 'dictionary_comment_delete'}).text("지우기")
				deletelink.appendTo(comment);
				deletelink.bind('click', $.proxyWithArgs(DictionaryCommentList.deleteComment, DictionaryCommentList, item, comment));
			}
		});
	},
	addToMultipleProfessor:function(obj)
	{
		var professor_tabs = $('#course-professor');
		var default_tab = $('<div>', {'class': 'course-professor-tab'}).text('일반');

		default_tab.appendTo(professor_tabs);
		default_tab.bind('click', $.proxyWithArgs(DictionaryCommentList.onChangeProfessor, DictionaryCommentList, null));

		$.each(obj, function(index, item) {
			var professor_tab = $('<div>', {'class': 'course-professor-tab'}).text(item.professor_name);
			professor_tab.appendTo(professor_tabs);
			
			professor_tab.bind('click', $.proxyWithArgs(DictionaryCommentList.onChangeProfessor, DictionaryCommentList, item));
		});
	},
	clearComment:function()
	{
		this.comments.empty();
		Data.DictionaryComment=[];
	},
	clearEval: function()
	{
		this.eval.empty();
	},
	clearSummary:function()
   	{
   		this.summary.empty();
   	},
	clearLectureSummary:function()
	{
		this.lecture_summary.empty();
	},
	update:function(obj)
	{
		Data.DictionaryComment = obj;
	},
	addToFront:function(obj)
	{
		Data.DictionaryComment = obj.concat(Data.DictionaryComment);
	},
	
	addToGeneralSummary:function(general_summary)
	{
		var top_div = $('<div>', {'id': 'course-summary-top'});
		var left_div = $('<div>', {'id': 'course-intro'});
		if (general_summary==null){
			var output_explain = "";
			var output_require = "";
		}
		else{
			var output_explain = general_summary.summary.replace(/\n/g,'<br />');
			var output_require = general_summary.prerequisite.replace(/\n/g,'<br />');	
		}

		$('<div>', {'id': 'course-subject'}).text(Data.Course.title).appendTo(left_div);
		$('<hr>',{'id': 'course-line'}).appendTo(left_div);
		$('<div>', {'id': 'course-explain-title'}).text(gettext("과목 설명")).appendTo(left_div);
		$('<div>', {'id': 'course-explain'}).html(output_explain).appendTo(left_div);
		$('<textarea>', {'id': 'course-explain-add'}).text(output_explain).appendTo(left_div);
		$('<div>', {'id': 'course-require-title'}).text(gettext("선수 과목")).appendTo(left_div);
		$('<div>', {'id': 'course-require'}).html(output_require).appendTo(left_div);
		$('<textarea>', {'id': 'course-require-add'}).text(output_require).appendTo(left_div);

		var right_div = $('<div>', {'id': 'course-score'});
		$('<div>', {'id': 'course-eval-title'}).text("TOTAL SCORE").appendTo(right_div);

		var right_div_eval = $('<div>', {'id': 'course-eval'});
		$('<div>', {'class': 'course-eval-score'}).text(gettext("학 점 ") + Data.Course.score_average.toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'course-eval-score'}).text(gettext("로 드 ") + Data.Course.load_average.toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'course-eval-score'}).text(gettext("남는거 ") + Data.Course.gain_average.toFixed(1)).appendTo(right_div_eval);
		right_div_eval.appendTo(right_div);

		$('<div>', {'id': 'course-eval-average'}).text(((Data.Course.score_average+Data.Course.load_average+Data.Course.gain_average)/3).toFixed(1)).appendTo(right_div);;
		$('<div>', {'id': 'course-eval-count'}).text(gettext("평가자 수 : ") + Data.Course.comment_num + gettext("명")).appendTo(right_div);

		left_div.appendTo(top_div);
		right_div.appendTo(top_div);
		var bottom_div = $('<div>', {'id': 'course-summary-bottom'});
		var add_img = $('<img>', {'src': 'http://bit.sparcs.org/~seal/OTL_project/%ea%b3%a0%ec%b9%a8%eb%b2%84%ed%8a%bc.gif', 'id': 'course-summary-add-img'});
		var complete_img = $('<img>', {'src': 'http://bit.sparcs.org/~seal/OTL_project/%ea%b3%a0%ec%b9%a8%eb%b2%84%ed%8a%bc.gif', 'id': 'course-summary-complete-img'});
		if(general_summary==null)
			var bottom_text = $('<div>', {'id': 'course-change-user'}).html("");
		else
			var bottom_text = $('<div>', {'id': 'course-change-user'}).html(gettext("마지막 고침 : ") + general_summary.written_datetime + " " + general_summary.writer + " ");

		add_img.appendTo(bottom_text);
		complete_img.appendTo(bottom_text);
		bottom_text.appendTo(bottom_div);
		add_img.bind('click', $.proxy(this.showSummary, this));
		complete_img.bind('click', $.proxy(this.addSummary, this));

		top_div.appendTo(this.summary);
		bottom_div.appendTo(this.summary);

		$('#course-explain-add').hide();
		$('#course-require-add').hide();
		$('#course-summary-complete-img').hide();
	},
	addToLectureSummary:function(obj)
	{
		var top_div = $('<div>', {'id': 'lecture-summary-top'});
		var left_div = $('<div>', {'id': 'lecture-intro'});
		if(obj.summary==null){
			var output_homepage = "";
			var output_mainbook = "";
			var output_subbook = "";
		}
		else{
			var output_homepage = obj.summary.homepage.replace(/\n/g,'<br />');
			var output_mainbook = obj.summary.main_material.replace(/\n/g,'<br />');
			var output_subbook = obj.summary.sub_material.replace(/\n/g,'<br />');
		}
		$('<div>', {'id': 'lecture-subject'}).text(Data.Course.title).appendTo(left_div);
		$('<hr>', {'id': 'lecture-line'}).appendTo(left_div);
		
		var prof_img = $('<img>', {'id': 'lecture-prof-img', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+Data.current_professor_id+'.jpg'});
		prof_img.appendTo(left_div);

		$('<div>', {'id': 'lecture-homepage-title'}).text(gettext("과목 홈페이지")).appendTo(left_div);
		$('<div>', {'id': 'lecture-homepage'}).html(output_homepage).appendTo(left_div);
		$('<textarea>', {'id': 'lecture-homepage-add'}).text(output_homepage).appendTo(left_div);
		$('<div>', {'id': 'lecture-mainbook-title'}).text(gettext("주교재")).appendTo(left_div);
		$('<div>', {'id': 'lecture-mainbook'}).html(output_mainbook).appendTo(left_div);
		$('<textarea>', {'id': 'lecture-mainbook-add'}).text(output_mainbook).appendTo(left_div);
		$('<div>', {'id': 'lecture-subbook-title'}).text(gettext("부교재")).appendTo(left_div);
		$('<div>', {'id': 'lecture-subbook'}).html(output_subbook).appendTo(left_div);
		$('<textarea>', {'id': 'lecture-subbook-add'}).text(output_subbook).appendTo(left_div);

		var right_div = $('<div>', {'id': 'lecture-score'});
		$('<div>', {'id': 'lecture-eval-title'}).text("TOTAL SCORE").appendTo(right_div);

		var right_div_eval = $('<div>', {'id': 'lecture-eval'});
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("학 점 ") + obj.average['avg_score'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("로 드 ") + obj.average['avg_load'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("남는거 ") + obj.average['avg_gain'].toFixed(1)).appendTo(right_div_eval);
		right_div_eval.appendTo(right_div);

		$('<div>', {'id': 'lecture-eval-average'}).text(((obj.average['avg_score']+obj.average['avg_load']+obj.average['avg_gain'])/3).toFixed(1)).appendTo(right_div);
		$('<div>', {'id': 'lecture-eval-count'}).text(gettext("평가자 수 : ") +obj.comment_num + gettext("명")).appendTo(right_div);

		left_div.appendTo(top_div);
		right_div.appendTo(top_div);
		var bottom_div = $('<div>', {'id': 'lecture-summary-bottom'});
		var add_img = $('<img>', {'src': 'http://bit.sparcs.org/~seal/OTL_project/%ea%b3%a0%ec%b9%a8%eb%b2%84%ed%8a%bc.gif', 'id': 'lecture-summary-add-img'});
		var complete_img = $('<img>', {'src': 'http://bit.sparcs.org/~seal/OTL_project/%ea%b3%a0%ec%b9%a8%eb%b2%84%ed%8a%bc.gif', 'id': 'lecture-summary-complete-img'});
		if(obj.summary==null)
			var bottom_text = $('<div>', {'id': 'lecture-change-user'}).html("");
		else
			var bottom_text = $('<div>', {'id': 'lecture-change-user'}).html(gettext("마지막 고침 : ") + obj.summary.written_datetime + " " + obj.summary.writer + " ");
		
		add_img.appendTo(bottom_text);
		complete_img.appendTo(bottom_text);
		bottom_text.appendTo(bottom_div);
		add_img.bind('click', $.proxy(this.showLectureSummary, this));
		complete_img.bind('click', $.proxy(this.addLectureSummary, this));

		top_div.appendTo(this.lecture_summary);
		bottom_div.appendTo(this.lecture_summary);

		$('#lecture-homepage-add').hide();
		$('#lecture-mainbook-add').hide();
		$('#lecture-subbook-add').hide();
		$('#lecture-summary-complete-img').hide();

	},
	onChangeProfessor:function(e,obj)
	{
		this.clearComment();
		this.clearSummary();
		this.clearLectureSummary();
		if(obj==null) {
			Data.current_professor_id = -1;
			Data.comment_id = -1;
		}
		else {
			Data.current_professor_id = obj.professor_id;
			Data.comment_id = -1;
		}
		$.ajax({
			type: 'POST',
			url: '/dictionary/get_summary/',
			data: {'professor_id': Data.current_professor_id,  'course_id' : Data.Course.id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if(resObj.result=="GENERAL"){
					    this.addToGeneralSummary(resObj.summary);
					}
					else if(resObj.result=="GEN_EMPTY")
					{
				            this.addToGeneralSummary(null);
					}
					else if(resObj.result=="PROF")
					{
					    this.addToLectureSummary(resObj);
					}
					else if(resObj.result=="PROF_EMPTY")
					{
					    resObj.summary=null;
					    this.addToLectureSummary(resObj);
					}
					this.showMoreComments();
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}	
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if(xhr.status == 403){
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else{
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},

    addNewComment:function(obj){
	    $.each(obj, function(index, item) {
	        var enableDelete = (item.writer_id == Data.user_id);
	        var comment = $('<div>', {'class': 'dictionary_comment'});
			var comment_output = item.comment.replace(/\n/g,'<br />');
	        comment.prependTo(DictionaryCommentList.comments);
	


	        $('<a>').text(item.writer_nickname).appendTo(comment);
	        $('<div>', {'class': 'dictionary_comment_content'}).html(comment_output).appendTo(comment);
	        $('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("학점") + ':' + item.score).appendTo(comment);
	        $('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("로드") + ':' + item.load).appendTo(comment);
	        $('<div>', {'class': 'dictionary_comment_eval'}).text(gettext("남는거") + ':' + item.gain).appendTo(comment);
	
	        if (enableDelete) {
	            var deletelink = $('<div>', {'class': 'dictionary_comment_delete'}).text("지우기")
	            deletelink.appendTo(comment);
	            deletelink.bind('click', $.proxyWithArgs(DictionaryCommentList.deleteComment, DictionaryCommentList, item, comment));
	        }
	    });
	
	},
};

var IndexLectureList = {
	initialize:function()
	{
		this.semesters = $(".show_taken_lecture");
		this.lecture_lists = $(".taken_lecture_list");
		this.lecture_titles = $(".taken_lecture_title");
		this.registerHandles();
		this.current_open = this.semesters.length-1;
	},
	registerHandles:function()
	{
		$.each(this.semesters, function(index, item) {
			$(item).bind('click', $.proxyWithArgs(IndexLectureList.showLectures, IndexLectureList, item));
		});
	},
	showLectures:function(e, obj)
	{
		$(IndexLectureList.lecture_lists[IndexLectureList.current_open]).hide();
		$(IndexLectureList.lecture_titles[IndexLectureList.current_open]).find('td').css("background-color","#DFE0E4")
		IndexLectureList.current_open = parseInt(obj.id)-1;
		$(IndexLectureList.lecture_lists[IndexLectureList.current_open]).show();
		$(IndexLectureList.lecture_titles[IndexLectureList.current_open]).find('td').css("background-color","#C0D9FD");
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
			data: {'count': max,},
			dataType: 'json',
			success: function (resObj) {
				//try {
					if (resObj.result=='OK') {
						this.comments = resObj.comments;
						IndexCommentList.addToMultipleComment(resObj.comments)
					}
					else {
						Notifier.setErrrorMsg(gettext('오류가 발생했습니다.'));
					}
				//} catch (e) {
				//	Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
				//}	
			},
			error: function (xhr) {
				Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
			}	   
		});
	},
	
    addToMultipleComment:function(obj)
	{
		var total = $(obj).length;
		$.each(obj, function(index, item) {
			var div_comment = $('<div>', {'class': 'timeline_comment'});
			div_comment.appendTo(IndexCommentList.timeline);

			var left_div_comment = $('<div>', {'class': 'timeline_comment_left'});
			var right_div_comment = $('<div>', {'class': 'timeline_comment_right'});

			left_div_comment.appendTo(div_comment);
			right_div_comment.appendTo(div_comment);

			$('<img>', {'class': 'content_prof_photo', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+item.professor[0].professor_id+'.jpg'}).appendTo(left_div_comment);
			$('<div>', {'class': 'content_prof_name'}).text(item.professor[0].professor_name).appendTo(left_div_comment);
			var right_top_div = $('<div>', {'class': 'timeline_comment_right_top'});
			var right_top_div_title = $('<div>',{'class':'timeline_comment_right_top_title'});
			var right_top_div_spec = $('<div>',{'class':'timeline_comment_right_top_spec'});
			
			right_top_div.appendTo(right_div_comment);
			right_top_div_title.appendTo(right_top_div);
			right_top_div_spec.appendTo(right_top_div);
		
			var right_mid_div = $('<div>', {'class': 'timeline_comment_right_mid'});
			var right_mid_div_comment = $('<div>',{'class':'timeline_comment_right_mid_comment'});
			
			right_mid_div.appendTo(right_div_comment);
			right_mid_div_comment.appendTo(right_mid_div);

			var comment_output = item.comment.replace(/\n/g,'<br/>');
		
			$('<a>', {'class': 'content_subject','href':'view/'+item.course_code+"/"}).text(item.course_title).appendTo(right_top_div_title);
			$('<div>', {'class': 'content_comment'}).html(comment_output).appendTo(right_mid_div_comment);
			$('<div>', {'class': 'a_spec'}).text('학점 :' + item.score).appendTo(right_top_div_spec);
			$('<div>', {'class': 'a_spec'}).text('로드 :' + item.load).appendTo(right_top_div_spec);
			$('<div>', {'class': 'a_spec'}).text('남는거 :' + item.gain).appendTo(right_top_div_spec);

			var right_bot_div = $('<div>',{'class':'timeline_comment_right_bot'});
    		var right_bot_div_writer = $('<div>',{'class':'timeline_comment_right_bot_writer'});
    		var right_bot_div_date = $('<div>',{'class':'timeline_comment_right_bot_date'});
    	
    		right_bot_div_writer.text('작성자 : '+ item.writer_nickname).appendTo(right_bot_div);	
    		right_bot_div_date.text(item.written_date).appendTo(right_bot_div);
    		right_bot_div.appendTo(right_div_comment);
    		right_bot_div_date.appendTo(right_bot_div);
    		right_bot_div_writer.appendTo(right_bot_div);
			if (index != total -1){
				$('<hr>',{'class': 'comment_line'}).appendTo(IndexCommentList.timeline);
			}
	});
	}
};	


var ProfessorCommentList = {
	initialize:function() 
	{
		this.comments = $('#comment-view');
		this.registerHandles();
		this.showComment();
		this.eval = $('#comment-avg');
                this.average = Data.Average;
	},
	registerHandles:function()
	{
	},
	showComment:function()
	{
		var max = NUM_ITEMS_PER_PROF_COMMENT;
		var conditions = {'count': max, 'prof_id': Data.ProfID};
		$.ajax ({
			type: 'POST',
			url: '/dictionary/professor_comment/',
			data: conditions,
			dataType: 'json',
			success: function (resObj) {
				try {
					if (resObj.result=='OK') {
						this.comments = resObj.comments;
						ProfessorCommentList.addToMultipleComment(resObj.comments)
					}
					else {
						Notifier.setErrrorMsg(gettext('오류가 발생했습니다.'));
					}
				} catch (e) {
                                    Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}	
			},
			error: function (xhr) {
                                if (suppress_ajax_errors)
                                        return;
				Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
			} 
		});
	},
        addToMultipleComment:function(obj)
	{
		$.each(obj, function(index, item) {
			var div_comment = $('<div>', {'class': 'professor_comment'});
			div_comment.appendTo(ProfessorCommentList.comments);

			$('<a>', {'class': 'content_subject'}).text("과목명:"+item.course_title+" ").appendTo(div_comment);
			$('<a>', {'class': 'content_comment'}).text("코멘트:"+item.comment+" ").appendTo(div_comment);
			$('<a>', {'class': 'content_score'}).text('학점:' + item.score).appendTo(div_comment);
			$('<a>', {'class': 'content_load'}).text('로드:' + item.load).appendTo(div_comment);
			$('<a>', {'class': 'content_gain'}).text('남는거:' + item.gain).appendTo(div_comment);
		});
		$('<a>').text('학점 : '+Data.Average.avg_score).appendTo(this.eval);
		$('<a>').text('로드 : '+Data.Average.avg_load).appendTo(this.eval);
		$('<a>').text('남는거 : '+Data.Average.avg_gain).appendTo(this.eval);
	}
}

var FavoriteList = {
	initialize:function() 
	{
		this.favorites = $('#favorite_view_contents');
		this.addToMultipleFavorite(Data.Favorites);
	},
	addToMultipleFavorite:function(obj)
	{
		$.each(obj, function(index, item) {
			var favorite = $('<div>', {'class': 'dictionary_favorite'});
			favorite.appendTo(FavoriteList.favorites);
			$('<a>', {'href': item.url}).text(item.code + ' - ' + item.title).appendTo(favorite);
			
			var deletelink = $('<a>').text(" X")
			deletelink.appendTo(favorite);
			deletelink.bind('click', $.proxyWithArgs(FavoriteList.deleteFavorite, FavoriteList, item, favorite));
		});
	},
	deleteFavorite:function(e,obj, favorite) 
	{
		$.ajax({
			type: 'POST',
			url: '/dictionary/delete_favorite/',
			data: {'course_id': obj.course_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='DELETE') {
                        favorite.remove();
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
	}
};

var FavoriteController = {
	initialize:function()
	{
		this.course_id =  Data.Course['id'];
		this.submitFavorite = $('input[name="addFavorite"]');
		this.registerHandles();
	},
	registerHandles:function()
	{
		$(this.submitFavorite).bind('click', $.proxy(this.addFavorite, this));

	},
	addFavorite:function(obj)
	{
		$.ajax({
			type: 'POST', 
			url: '/dictionary/add_favorite/',
			data: {'course_id': this.course_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='ADD') {
						Notifier.setErrorMsg(gettext('추가되었습니다.'));
					} else if (resObj.result='ALREADY_ADDED') {
						Notifier.setErrorMsg(gettext('이미 추가하셨습니다.'));
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
	},

};
