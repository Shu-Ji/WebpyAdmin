var ONE = 1, TWO = 2, THREE = 4;


$(function(){
    try{$('textarea').autosize();}catch(e){}
    $('[title]').tooltip({placement: 'bottom'});
    // 去除所有不能排序的字段的三角形
    $('tbody tr:first td').filter(':not(:has(span))').each(function(i, v){
        $('i', $('thead th:eq(' + $(v).index() + ')').addClass('no-sort')).remove();
    });
    var $toolbar = $('.toolbar');
    // 表头排序
    var $content = $('#content').on('click', 'thead tr th:not(.no-sort)', function(){
        var self = $(this);
        var $table = self.parents('table:first');
        var $i = self.find('i').toggleClass('icon-sort-up icon-sort-down').removeClass('gray');
        var col = getColumn($('tbody tr:first td', $table).filter(':eq(' + self.index() + ')').children(':first'), THREE);
        if(col == null){
            // 不能排序的字段（如密码，文件字段等）
            $i.remove();
            return;
        }
        $('i', self.siblings()).addClass('gray');
        var asc = {true: 'asc', false: 'desc'};
        col = col + ' ' + asc[$i.hasClass('icon-sort-up')];
        $.get(location.href + '?order=' + col, function(html){
            $table.find('tbody').replaceWith($(html).find('tbody'));
        });
    }).on('mouseenter', 'tbody tr', function(e){
        var id = getColumn($toolbar.removeClass('hide').appendTo($(this).children(':last'))
        .parents('tr:first').find('[id*="-"]'), TWO);
        var pre = location.href + '/';
        $('a:first', $toolbar).attr('href', pre + 'modify/' + id);
        $('a:eq(1)', $toolbar).attr('href', pre + 'add');
        $('a:last', $toolbar).data('href', pre + 'delete/' + id);
    }).on('mouseleave', 'tbody tr', function(e){
        $toolbar.addClass('hide');
    });
    // 修改页面
    $('.btn.mod').click(function(){
        var self = $(this);
        if(isSubmiting(self)){
            return;
        }
        var $form = self.parents('form:first');
        blockSubmit(self);
        $.post(location.href, $form.serialize(), function(jsn){
            unblockSubmit(self);
            showMsg(jsn);
        });
    });
    // 添加
    $('.btn.add').click(function(){
        var self = $(this);
        if(isSubmiting(self)){
            return;
        }
        var $form = self.parents('form:first');
        blockSubmit(self);
        $.post(location.href, $form.serialize(), function(jsn){
            unblockSubmit(self);
            showMsg(jsn);
        });
    });
    // 删除
    $content.on('click', 'li a.del', function(){
        var self = $(this);
        if(!window.confirm('确认删除吗？')){
            return false;
        }
        $.post(self.data('href'), function(jsn){
            if(showMsg(jsn)){
                // 删除本行
                self.parents('tr:first').remove();
            }
        });
        return false;
    });
    // 选择要扭过的字段
    $('a[data-c]').click(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
    // 搜索
    $('#q').next().click(function(){
        var self = $(this);
        var col = $('.active[data-c]');
        if(isSubmiting(self)){
            return;
        }
        if(col.length != 1){
            alert('请选择一个要搜索的字段');
            return;
        }
        var q = $('#q').val();
        if(q.length == 0){
            alert('请输入搜索的内容');
            return;
        }
        col = col.data('c');
        blockSubmit(self);
        $.post(location.href + '/search', {q: q, col: col}, function(jsn){
            var $table =$('.search-result').empty();
            unblockSubmit(self);
            if(jsn.suc){
                var $html = $(jsn.suc);
                $('thead tr th', $html).addClass('no-sort').children('i').remove();
                $table.append($html);
            }else{
                $table.append('无记录');
            }
        });
    });
});


function showMsg(jsn){
    if(jsn.suc){
        alert('成功。');
        return true;
    }else{
        alert('失败。');
        return false;
    }
}


function getColumn(e, index){
    try{
        var col = $(e).attr('id').split('-');
    }catch(e){
        return null;
    }
    var table = [ONE, TWO, THREE];
    var idx = table.indexOf(index);
    if(idx != -1){
        return col[idx];
    }else if(index == ONE + TWO){
        return [col[0], col[1]];
    }else if(index == ONE + THREE){
        return [col[0], col[2]];
    }else if(index == TWO + THREE){
        return [col[1], col[2]];
    }
}


// 是否正在提交
function isSubmiting(btn){
    var $btn = $(btn);
    if($btn.data('block') === 'blocked'){
        return true;
    }
}


// 防止多次提交
function blockSubmit(btn){
    var $btn = $(btn);
    $btn.data('block', 'blocked').data('val', $btn.text()).
        addClass('disabled').
        html('<i class="icon-spinner icon-spin"></i> 稍等片刻...');
}


// 恢复提交按钮
function unblockSubmit(btn){
    var $btn = $(btn);
    $btn.data('block', null).removeClass('disabled').text($btn.data('val'));
}
