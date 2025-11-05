import cv2
import numpy as np
from tqdm import tqdm

def resample_video(input_path, output_path, target_fps=30):
    """Resamplea el video a target_fps."""
    cap = cv2.VideoCapture(input_path)
    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    # Duración original
    duration = len(frames) / orig_fps
    new_frame_count = int(duration * target_fps)

    # Re-sample temporalmente
    indices = np.linspace(0, len(frames) - 1, new_frame_count).astype(int)
    resampled_frames = [frames[i] for i in indices]

    # Guardar video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))
    for f in resampled_frames:
        out.write(f)
    out.release()

    return output_path


def blend_frames(frames, window=15, method="uniform"):
    """
    Realiza un fundido de frames.
    - method: 'uniform' o 'weighted'
    """
    n = len(frames)
    blended_frames = []

    # Precomputar pesos
    if method == "weighted":
        # ventana gaussiana centrada
        sigma = window / 2
        distances = np.arange(-window, window + 1)
        weights = np.exp(-0.5 * (distances / sigma) ** 2)
        weights /= weights.sum()
    else:
        weights = np.ones(2 * window + 1) / (2 * window + 1)

    for i in tqdm(range(n), desc=f"Blending ({method})"):
        # rangos de frames vecinos
        idx_start = max(0, i - window)
        idx_end   = min(n - 1, i + window)

        # indices con padding si hace falta
        indices = np.arange(i - window, i + window + 1)
        indices = np.clip(indices, 0, n - 1)

        # obtener y combinar frames
        neighborhood = [frames[j] for j in indices]
        stack = np.stack(neighborhood, axis=0).astype(np.float32)

        # aplicar pesos
        current_weights = weights[:len(neighborhood)]
        weighted = (stack * current_weights[:, None, None, None]).sum(axis=0)
        blended_frames.append(np.clip(weighted, 0, 255).astype(np.uint8))

    return blended_frames


def process_video(input_path, output_path, method="uniform", fps=30, window=15):
    # 1. Resamplear
    print("→ Resampleando a 30 fps...")
    resampled_path = "_temp_resampled.mp4"
    resample_video(input_path, resampled_path, target_fps=fps)

    # 2. Cargar frames
    cap = cv2.VideoCapture(resampled_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    # 3. Fundido
    blended_frames = blend_frames(frames, window=window, method=method)

    # 4. Guardar resultado
    h, w = blended_frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    for f in blended_frames:
        out.write(f)
    out.release()
    print(f"✅ Video generado: {output_path}")


if __name__ == "__main__":
    # Ejemplo de uso:
    input_video = "gettingintocar_robbery_long"
    path = "videos/" + input_video + ".mp4"
    output_video_uniform = input_video + "_uniform.mp4"
    output_video_weighted = input_video + "_weighted.mp4"

    # Uniforme
    #process_video(input_video, output_video_uniform, method="uniform")

    # Ponderado
    process_video(path, output_video_weighted, method="weighted")
