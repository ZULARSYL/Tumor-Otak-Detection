processButton.addEventListener('click', async function () {
    if (fileInput.files.length === 0) {
        alert('Harap pilih file MRI terlebih dahulu.');
        return;
    }

    processButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Memproses...';
    processButton.disabled = true;

    const formData = new FormData();
    formData.append("image", fileInput.files[0]); // HARUS "image"

    try {
        const response = await fetch("/process-image", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Gagal memproses gambar");
        }

        // Terima hasil sebagai blob (image)
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        // Tampilkan hasil
        processedImage.src = imageUrl;
        resultContainer.style.display = "block";

        detectionResults.innerHTML = `
            <div class="alert alert-info">
                <h5><i class="fas fa-brain me-2"></i>Hasil Deteksi YOLO</h5>
                <p class="mb-0">
                    Gambar telah diproses menggunakan model <b>YOLO (best.pt)</b>.
                    Bounding box dan label ditampilkan langsung pada gambar hasil.
                </p>
            </div>
        `;

        resultContainer.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        alert("Terjadi kesalahan saat inferensi");
        console.error(error);
    }

    processButton.innerHTML = '<i class="fas fa-play-circle me-2"></i>Proses Deteksi Tumor';
    processButton.disabled = false;
});
