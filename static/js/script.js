/**
 * Forest Weather Index (FWI) Prediction - Frontend Interactions
 * Vanilla JavaScript (Zero External Dependencies)
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("fwiForm");
  const submitBtn = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const clientAlert = document.getElementById("clientAlert");
  const clientAlertMsg = document.getElementById("clientAlertMsg");

  // Sample presets for quick testing and demonstration
  const presets = {
    low: {
      Temperature: "26.0",
      RH: "80.0",
      Ws: "12.0",
      Rain: "3.2",
      FFMC: "45.0",
      DMC: "4.5",
      ISI: "0.6",
      Classes: "0",
      Region: "0"
    },
    high: {
      Temperature: "37.5",
      RH: "36.0",
      Ws: "19.0",
      Rain: "0.0",
      FFMC: "89.5",
      DMC: "25.4",
      ISI: "9.8",
      Classes: "1",
      Region: "1"
    }
  };

  // Populate preset values
  window.loadPreset = function (type) {
    if (!form || !presets[type]) return;
    const data = presets[type];

    Object.keys(data).forEach((key) => {
      const field = form.elements[key];
      if (field) {
        field.value = data[key];
        // Trigger subtle visual pulse
        field.style.borderColor = "#10b981";
        setTimeout(() => {
          field.style.borderColor = "";
        }, 400);
      }
    });

    hideAlert();
  };

  // Reset form inputs
  window.resetForm = function () {
    if (!form) return;
    form.reset();
    hideAlert();
  };

  function showAlert(message) {
    if (clientAlert && clientAlertMsg) {
      clientAlertMsg.textContent = message;
      clientAlert.style.display = "flex";
      clientAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      alert(message);
    }
  }

  function hideAlert() {
    if (clientAlert) {
      clientAlert.style.display = "none";
    }
  }

  // Handle Form Submission
  if (form) {
    form.addEventListener("submit", (e) => {
      hideAlert();

      // Check required fields and numerical validity
      const requiredFields = [
        { name: "Temperature", min: -20, max: 60, label: "Temperature" },
        { name: "RH", min: 0, max: 100, label: "Relative Humidity" },
        { name: "Ws", min: 0, max: 120, label: "Wind Speed" },
        { name: "Rain", min: 0, max: 300, label: "Rainfall" },
        { name: "FFMC", min: 0, max: 105, label: "Fine Fuel Moisture Code" },
        { name: "DMC", min: 0, max: 500, label: "Duff Moisture Code" },
        { name: "ISI", min: 0, max: 150, label: "Initial Spread Index" },
        { name: "Classes", min: 0, max: 1, label: "Fire Classification" },
        { name: "Region", min: 0, max: 1, label: "Region" }
      ];

      for (const field of requiredFields) {
        const input = form.elements[field.name];
        if (!input || input.value.trim() === "") {
          e.preventDefault();
          showAlert(`Please fill in the ${field.label} field.`);
          if (input) input.focus();
          return;
        }

        const val = parseFloat(input.value);
        if (isNaN(val)) {
          e.preventDefault();
          showAlert(`Please enter a valid number for ${field.label}.`);
          input.focus();
          return;
        }

        if (val < field.min || val > field.max) {
          e.preventDefault();
          showAlert(
            `${field.label} must be between ${field.min} and ${field.max}.`
          );
          input.focus();
          return;
        }
      }

      // Valid form -> Trigger loading state to prevent accidental double submissions
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add("is-submitting");
        if (btnText) {
          btnText.textContent = "Computing Prediction...";
        }
      }

      // Explicitly submit after disabling to ensure submission triggers
      form.submit();
    });
  }
});
