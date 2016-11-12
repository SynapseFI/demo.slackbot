const tabs = ['tab1', 'tab2', 'tab3'];
let activeTab = 0;

$(function() {
  bindListeners();
});

const bindListeners = function() {
  $('.back').click(function() {
    if (activeTab > 0) {
      $('.'+tabs[activeTab]).removeClass('active')
      activeTab -= 1;
      $('.'+tabs[activeTab]).addClass('active')
    }
  })

  $('.next').click(function() {
    if (activeTab < 2) {
      $('.'+tabs[activeTab]).removeClass('active')
      activeTab += 1;
      $('.'+tabs[activeTab]).addClass('active')
    }
  })
};
