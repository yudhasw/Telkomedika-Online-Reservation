document.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('.otp-input');
  const hiddenInput = document.getElementById('otp_full');
  const form = document.getElementById('otpForm');

  const updateHiddenInput = () => {
      let otpValue = '';
      inputs.forEach(input => otpValue += input.value);
      hiddenInput.value = otpValue;
  };

  inputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
          e.target.value = e.target.value.replace(/[^0-9]/g, '');
          if (e.target.value.length === 1 && index < inputs.length - 1) inputs[index + 1].focus();
          updateHiddenInput();
      });
      input.addEventListener('keydown', (e) => {
          if (e.key === 'Backspace') {
              if (e.target.value === '' && index > 0) inputs[index - 1].focus();
              else e.target.value = '';
              updateHiddenInput();
          }
      });
  });

  form.addEventListener('submit', (e) => {
      updateHiddenInput();
      if (hiddenInput.value.length < 4) {
          e.preventDefault();
          alert("Silakan lengkapi 4 digit kode OTP.");
      }
  });

  function startTimer(duration, display) {
      var timer = duration, minutes, seconds;
      setInterval(function () {
          minutes = parseInt(timer / 60, 10);
          seconds = parseInt(timer % 60, 10);
          minutes = minutes < 10 ? "0" + minutes : minutes;
          seconds = seconds < 10 ? "0" + seconds : seconds;
          display.textContent = minutes + ":" + seconds;
          if (--timer < 0) timer = 0;
      }, 1000);
  }
  window.onload = function () { startTimer(60 * 2, document.querySelector('#countdown')); };
});