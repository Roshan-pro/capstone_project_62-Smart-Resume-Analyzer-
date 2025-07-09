function analyzeResume() {
  const fileInput = document.getElementById("resume");
  const file = fileInput.files[0];

  // --- Validation ---
  if (!file) {
    alert("Please upload a PDF file first.");
    return;
  }

  if (file.type !== "application/pdf") {
    alert("Only PDF files are allowed.");
    return;
  }

  // --- Show Spinner, Hide Result ---
  document.getElementById("loading-spinner").classList.remove("hidden");
  document.getElementById("result-box").classList.add("hidden"); 

  const formData = new FormData();
  formData.append("resume", file);

  fetch("/analyze", {
    method: "POST",
    body: formData,
  })

    .then((response) => {
      if (!response.ok) {
        throw new Error("Server returned an error.");
      }
      return response.json();
    })
    .then((data) => {
      document.getElementById("loading-spinner").classList.add("hidden");
      document.getElementById("result-box").classList.remove("hidden");

      document.getElementById("score").innerText = `Resume Score: ${data.score}`;
      document.getElementById("tips").innerText = `Suggestions:\n${data.tips}`;
      document.getElementById("predicted_category").innerText = `Predicted Category: ${data.predicted_category}`;

      // Format jobs
      const jobList = data.jobs.map((job, i) =>
        `${i + 1}. ${job.title} at ${job.company}, ${job.location}\nApply: ${job.link}`
      ).join("\n\n");

      document.getElementById("jobs").innerText = `Jobs:\n${jobList}`;
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Something went wrong. Make sure the backend is running.");
      document.getElementById("loading-spinner").classList.add("hidden");
    });
}

// Feedback form submission via AJAX

document.addEventListener("DOMContentLoaded", function () {
  const feedbackForm = document.querySelector('#contact form');
  if (feedbackForm) {
    feedbackForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const name = feedbackForm.querySelector('input[type="text"]').value.trim();
      const email = feedbackForm.querySelector('input[type="email"]').value.trim();
      const message = feedbackForm.querySelector('textarea').value.trim();
      if (!name || !email || !message) {
        alert('Please fill in all fields.');
        return;
      }
      fetch('/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message })
      })
        .then(res => {
          if (!res.ok) throw new Error('Server error');
          return res.json();
        })
        .then(data => {
          alert('Thank you for your feedback!');
          feedbackForm.reset();
        })
        .catch(() => {
          alert('Could not send feedback. Please try again later.');
        });
    });
  }
});
