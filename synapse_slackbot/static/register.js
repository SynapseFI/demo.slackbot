$(function() {
  const testing = true;
  if (testing) prefillFields(); 
  bindListeners();
});

const TABS = ['tab0', 'tab1', 'tab2', 'tab3'];
let activeTab = 0;
const lastTab = TABS.length - 1;

const activeTabSelector = function(tabNumber) {
  return '.' + TABS[activeTab];
};

const bindListeners = function() {
  bindListenerBackButton();
  bindListenerNextButton();
  bindListenerInputChange();
  bindGoogleAddressAutocomplete();
  bindListenerFileInput();
  bindListenersEditButtons();
  bindListenerFormSubmit();
};


// EVENT LISTENERS

const bindListenerBackButton = function() {
  $('.back').click(function(e) {
    e.preventDefault();
    tabBackwards();
  });
};

const bindListenerNextButton = function() {
  $('.next').click(function(e) {
    e.preventDefault();

    if (checkValidationErrors().length > 0) {
      return;
    }

    tabForwards();
  });
};

const bindListenerInputChange = function() {
  $('form').bind('keyup click change', function() {
    if (checkAllTabInputsFilled()) {
      enableNextButton();
    }
    else {
      disableNextButton();
    }
  });
};

let base64;
const bindListenerFileInput = function() {
  $('#govtId').on('change', function(e){
    fileToBase64(this.files[0], function(e) {
      base64 = (e.target.result);
    });
  });
};

let autocomplete;
const bindGoogleAddressAutocomplete = function() {
  const input = document.getElementById('address');
  const options = {
    types: ['address'],
    componentRestrictions: {country: 'us'}
  };

  autocomplete = new google.maps.places.Autocomplete(input, options);
};

const bindListenersEditButtons = function() {
  $('#editTab0').on('click', function(e) {
    e.preventDefault();
    setActiveTab(0);
  });
  $('#editTab1').on('click', function(e) {
    e.preventDefault();
    setActiveTab(1);
  });
  $('#editTab2').on('click', function(e) {
    e.preventDefault();
    setActiveTab(2);
  });
};

const bindListenerFormSubmit = function() {
  $('form').submit(function(e) {
    e.preventDefault();
    clearAlerts();
    transmitFormData(this);
  });
};


// TAB NAV / BUTTON BEHAVIOR

const setActiveTab = function(tabNumber) {
  hideActiveTab();
  activeTab = tabNumber;
  showActiveTab();

  if (activeTab === 0) {
    disableBackButton();
  }
  else {
    enableBackButton();
  }

  if (activeTab === lastTab) {
    populateReviewFields();
    showSubmit();
  }
  else {
    hideSubmit();
  }
};

const tabBackwards = function() {
  clearAlerts();
  setActiveTab(activeTab - 1);
};

const tabForwards = function() {
  clearAlerts();
  disableNextButton();
  setActiveTab(activeTab + 1);
};

const hideActiveTab = function() {
  $(activeTabSelector()).removeClass('active');
};

const showActiveTab = function() {
  $(activeTabSelector()).addClass('active');
};

const enableBackButton = function() {
  $('.back').removeAttr('disabled');
};

const disableBackButton = function () {
  $('.back').attr('disabled', true);
};

const enableNextButton = function() {
  $('.next').removeAttr('disabled');
};

const disableNextButton = function() {
  $('.next').attr('disabled', true);
};

const hideSubmit = function() {
  $('.next').removeClass('inactive');
  enableNextButton();
  $('.submit').addClass('inactive');
  $('.submit').attr('disabled', true);
};

const showSubmit = function() {
  $('.next').addClass('inactive');
  disableNextButton();
  $('.submit').removeClass('inactive');
  $('.submit').removeAttr('disabled');
};

const checkAllTabInputsFilled = function() {
  const $inputs = $(activeTabSelector() + ' input');
  let filled = true;
  $inputs.each(function(index, element) {
    if ($(element).val() == '') {
      filled = false;
    }
  });
  return filled;
};

const populateReviewFields = function() {
  $('#review_name').text($('input[name=name]').val()),
  $('#review_birthday').text($('input[name=birthday]').val());
  $('#review_email').text($('input[name=email]').val());
  $('#review_phone').text($('input[name=phone]').val());
  $('#review_address').text($('input[name=address]').val());
  $('#review_ssn').text($('input[name=ssn]').val());
  $('#review_govt_id').text($('input[name=govt_id').val());
  $('#review_account_number').text($('input[name=account_number]').val());
  $('#review_routing_number').text($('input[name=routing_number]').val());
};


// FORM SUBMISSION

const transmitFormData = function(form) {
  const formData = prepFormData(form);
  renderAlert('Please wait...', 'pending');

  $.ajax({
    url: $(this).attr('action'),
    method: 'POST',
    data: formData,
    processData: false,
    contentType: false,
    dataType: 'json'
  })
    .done(function(data) {
      handleSuccess(data);
    })
    .fail(function(data) {
      handleFailure(data);
    });
};

const prepFormData = function(form) {
  const formData = new FormData(form);
  const address = parseAddressFromAutocomplete(autocomplete);
  formData.set('address_street', address.street);
  formData.set('address_city', address.city);
  formData.set('address_state', address.state);
  formData.set('address_zip', address.zip);
  formData.append('file', base64);
  return formData;
};

const handleSuccess = function(data) {
  clearAlerts();
  renderAlert(data['message'], 'valid');
};

const handleFailure = function(data) {
  clearAlerts();
  const errorText = JSON.parse(data['responseText'])['message'];
  renderAlert(errorText, 'invalid');
};


// INPUT VALIDATION

const checkValidationErrors = function() {
  if (activeTab === 0) {
    return tab0Validations();
  }
  else if (activeTab === 1) {
    return tab1Validations();
  }
  else if (activeTab === 2) {
    return tab2Validations();
  }
};

const tab0Validations = function() {
  const fields = {
    $name: $('input[name=name]'),
    $birthday: $('input[name=birthday]'),
    $email: $('input[name=email]'),
    $phone: $('input[name=phone]'),
    $address: $('input[name=address]')
  };

  resetFieldHighlighting(fields);

  const errors = [];

  if (fields.$name.val().split(' ').length < 2) {
    errors.push('Name must be at least 2 words.');
    fields.$name.addClass('invalid');
  }
  if (fields.$birthday.val().length < 10) {
    errors.push('Invalid date of birth.');
    fields.$birthday.addClass('invalid');
  }
  if (!/\S+@\S+\.\S+/.test(fields.$email.val())) {
    errors.push('Invalid email address.');
    fields.$email.addClass('invalid');
  }
  if (fields.$phone.val().length < 10) {
    errors.push('Phone number must be at least 10 digits.');
    fields.$phone.addClass('invalid');
  }
  if (fields.$address.val().split(' ').length < 2) {
    errors.push('Invalid address.');
    fields.$address.addClass('invalid');
  }
  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab1Validations = function() {
  const fields = {
    $ssn: $('input[name=ssn]'),
    $govtId: $('input[name=govt_id')
  };

  resetFieldHighlighting(fields);

  const errors = [];

  if (fields.$ssn.val().length < 4) {
    errors.push('SSN must be at least 4 digits.');
    fields.$ssn.addClass('invalid');
  }
  if (fields.$govtId.val().length < 4) {
    errors.push('Photo ID image required.');
    fields.$govtId.addClass('invalid');
  }

  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab2Validations = function() {
  const fields = {
    $accountNumber: $('input[name=account_number]'),
    $routingNumber: $('input[name=routing_number]')
  };

  resetFieldHighlighting(fields);

  const errors = [];

  if (fields.$accountNumber.val() < 6) {
    errors.push('Account number must be at least 6 digits.');
    fields.$accountNumber.addClass('invalid');
  }
  if (fields.$routingNumber.val().length !== 9) {
    errors.push('Routing number must be 9 digits.');
    fields.$routingNumber.addClass('invalid');
  }

  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const resetFieldHighlighting = function(fields) {
  $.each(fields, function(_, $input) {
    $input.removeClass('invalid');
  });
};


// ALERT MESSAGES

const alertMessage = function(text) {
  return $('<p class="alert-message">' + text + '</p>');
};

const renderErrors = function(errors) {
  const $errorElements = errors.forEach(function(errorText){
    renderAlert(errorText, 'invalid');
  });
};

const clearAlerts = function() {
  const $alert = $('.alert');
  $alert.empty();
  $alert.removeClass('valid invalid pending');
};

const renderAlert = function(message, status) {
  const $alert = $('.alert');
  $alert.append(alertMessage(message));
  $alert.removeClass('valid invalid pending');
  $alert.addClass(status);
};


// HELPERS

const fileToBase64 = function(file, onLoadCallback){
  const reader = new FileReader();
  reader.onload = onLoadCallback;
  return reader.readAsDataURL(file);
};

const parseAddressFromAutocomplete = function(autocomplete) {
  const addressFields = autocomplete.gm_accessors_.place.Fc.place.address_components;
  const street = [addressFields[0].short_name, addressFields[1].short_name].join(' ');
  const city = addressFields[3].long_name;
  const state = addressFields[5].short_name;
  const zip = addressFields[7].short_name;
  return {
    street: street,
    city: city,
    state: state,
    zip: zip
  };
};


// FOR TESTING

const prefillFields = function() {
  const $name = $('input[name=name]'),
    $birthday = $('input[name=birthday]'),
    $email = $('input[name=email]'),
    $phone = $('input[name=phone]'),
    $address = $('input[name=address]'),
    $ssn = $('input[name=ssn]'),
    $govtId = $('input[name=govt_id'),
    $accountNumber = $('input[name=account_number]'),
    $routingNumber = $('input[name=routing_number]');

  $name.val('Steven Broderick');
  $birthday.val('1900-03-19');
  $email.val('steven@synapsepay.com');
  $phone.val('5555555555');
  $address.val('123 Main St, San Francisco, CA 94119');
  $ssn.val('2222');
  $accountNumber.val('12345678');
  $routingNumber.val('123456789');
};
