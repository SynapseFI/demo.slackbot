const tabs = ['tab1', 'tab2', 'tab3'];
let activeTab = 0;

$(function() {
  bindListeners();
});

const bindListeners = function() {
  bindBackButton();
  bindNextButton();
  bindFormSubmit();
};

const bindBackButton = function() {
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
};

const bindNextButton = function() {
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
};

const bindFormSubmit = function() {
  $('form').submit(function() {
    console.log(this)
    const url = this.attr('action')
    const request = $.ajax({
      url: url,
      method: 'POST',
      data: this.serialize(),
      dataType: 'json'
    });
  });
};
