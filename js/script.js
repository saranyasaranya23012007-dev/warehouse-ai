
document.addEventListener("DOMContentLoaded", function () {

  // 1. Highlight current navigation link
  const currentPage =
    window.location.pathname.split("/").pop() || "index.html";

  document.querySelectorAll(".nav-link").forEach(function (link) {
    link.classList.toggle(
      "active",
      link.getAttribute("href") === currentPage
    );
  });

  // 2. Handle unavailable warehouse photos
  document.querySelectorAll("img").forEach(function (image) {
    image.addEventListener("error", function () {
      image.style.background = "#e5eee7";
      image.style.minHeight = "120px";
      image.alt = "Warehouse photo unavailable. Check your internet connection.";
    });
  });

  // 3. Image upload and preview
  const fileInput = document.getElementById("warehouseFile");
  const preview = document.getElementById("imagePreview");
  const fileMessage = document.getElementById("fileMessage");
  const analyzeButton = document.getElementById("analyzeButton");
  const uploadStatus = document.getElementById("uploadStatus");

  let previewUrl = null;

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const file = fileInput.files[0];

      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        previewUrl = null;
      }

      if (!file) {
        if (fileMessage) {
          fileMessage.textContent = "No image selected.";
        }

        if (preview) preview.style.display = "none";
        if (analyzeButton) analyzeButton.disabled = true;
        return;
      }

      if (!file.type.startsWith("image/")) {
        if (fileMessage) {
          fileMessage.textContent = "Please select an image file.";
        }

        fileInput.value = "";
        if (analyzeButton) analyzeButton.disabled = true;
        if (preview) preview.style.display = "none";
        return;
      }

      previewUrl = URL.createObjectURL(file);

      if (preview) {
        preview.src = previewUrl;
        preview.style.display = "block";
      }

      if (fileMessage) {
        fileMessage.textContent =
          file.name + " (" + (file.size / 1024).toFixed(1) + " KB)";
      }

      if (analyzeButton) analyzeButton.disabled = false;

      if (uploadStatus) {
        uploadStatus.textContent =
          "Image selected successfully. Click Analyze to detect objects.";
      }
    });
  }

  // 4. Connect Analyze button to FastAPI backend
  if (analyzeButton) {
    analyzeButton.addEventListener("click", async function () {

      if (!fileInput || !fileInput.files.length) {
        alert("Please select a warehouse image first.");
        return;
      }

      const file = fileInput.files[0];
      const formData = new FormData();

      formData.append("file", file);

      analyzeButton.disabled = true;
      analyzeButton.textContent = "Analyzing...";

      if (uploadStatus) {
        uploadStatus.textContent = "AI is analyzing your image. Please wait...";
      }

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/detect",
          {
            method: "POST",
            body: formData
          }
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || "Detection failed");
        }

        const objects = result.detected_objects;
        const objectNames = Object.entries(objects);

        let output = "Detection completed successfully!\n";

        if (objectNames.length === 0) {
          output += "No objects detected.";
        } else {
          objectNames.forEach(function ([name, count]) {
            output += "\n" + name + ": " + count;
          });
        }

        if (uploadStatus) {
          uploadStatus.textContent = output;
        }

      } catch (error) {
        if (uploadStatus) {
          uploadStatus.textContent = "Error: " + error.message;
        }

        console.error("Detection error:", error);

      } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Image";
      }
    });
  }

});
