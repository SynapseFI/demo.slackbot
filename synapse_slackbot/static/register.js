const tabs = ['tab1', 'tab2', 'tab3'];
let activeTab = 0;

$(function() {
  bindListeners();
});

const bindListeners = function() {
  $('.back').click(function() {
    if (activeTab > 0) {
      $('.'+tabs[activeTab]).removeClass('active')
      if (activeTab === 2) {
        $('.next').removeClass('inactive')
        $('.submit').addClass('inactive')
      }
      activeTab -= 1;
      $('.'+tabs[activeTab]).addClass('active')
    }
  });

  $('.next').click(function() {
    if (activeTab < 2) {
      $('.'+tabs[activeTab]).removeClass('active')
      activeTab += 1;
      $('.'+tabs[activeTab]).addClass('active')
      if (activeTab === 2) {
        $('.next').addClass('inactive')
        $('.submit').removeClass('inactive')
      }
    }
  });

  $('form').submit(function() {
    const url = this.attr('action')
    debugger
    const request = $.ajax({
      url: url,
      method: 'POST',
      data: this.serialize(),
      dataType: 'json'
    });
  });
};


