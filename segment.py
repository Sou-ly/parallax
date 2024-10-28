from rembg import remove
from PIL import Image
import numpy as np
import os
import argparse
import cv2

def segment_image(input_path, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # Load and process the image
        input_image = Image.open(input_path)
        
        # Remove background and get RGBA result
        output = remove(input_image)
        
        # Create paths for all output files
        character_path = os.path.join(output_dir, f"{base_name}_character.png")
        background_path = os.path.join(output_dir, f"{base_name}_background.png")
        mask_path = os.path.join(output_dir, f"{base_name}_mask.png")
        
        # Save the character with transparent background
        output.save(character_path)
        
        # Create and save the binary mask
        mask = output.split()[3]  # Get alpha channel
        mask.save(mask_path)
        
        # Create the background image by removing the character
        # Convert mask to numpy array
        mask_np = np.array(mask)
        input_np = np.array(input_image)
        
        # Create inverted mask for background
        inv_mask = (255 - mask_np) / 255.0
        
        # Apply inverted mask to get background
        background = input_np.copy()
        for i in range(3):  # Apply to each RGB channel
            background[:,:,i] = background[:,:,i] * inv_mask
            
        # Convert back to PIL Image and save
        background_img = Image.fromarray(background)
        background_img.save(background_path)
        
        print(f"Segmented character saved to: {character_path}")
        print(f"Background saved to: {background_path}")
        print(f"Binary mask saved to: {mask_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def interpolate_position(keypoints, frame_index, frame_rate):
    """Calculate the interpolated position for the given frame based on keypoints."""
    current_time = frame_index / frame_rate  # Current timestamp in seconds

    # Find the two keypoints to interpolate between
    for i in range(len(keypoints) - 1):
        t1, pos1 = keypoints[i]
        t2, pos2 = keypoints[i + 1]

        if t1 <= current_time <= t2:
            # Linear interpolation
            fraction = (current_time - t1) / (t2 - t1)
            x = int(pos1[0] + fraction * (pos2[0] - pos1[0]))
            y = int(pos1[1] + fraction * (pos2[1] - pos1[1]))
            return x, y

    # If no interpolation point is found (i.e., time exceeds last keypoint), return the last position
    return keypoints[-1][1]

def translate_character(character_path, background_path, output_dir, position, frame_index):
    try:
        # Load character and background images
        character_img = Image.open(character_path).convert("RGBA")
        background_img = Image.open(background_path).convert("RGBA")
        
        # Create a blank canvas the size of the background
        canvas = Image.new("RGBA", background_img.size)
        
        # Paste the character image onto the canvas at the calculated position
        canvas.paste(character_img, position, character_img)
        
        # Composite the canvas onto the background image
        result = Image.alpha_composite(background_img, canvas)
        
        # Save each frame as a numbered PNG file
        frame_path = os.path.join(output_dir, f"frame_{frame_index:04d}.png")
        result.save(frame_path)
        
        print(f"Frame {frame_index} saved to: {frame_path}")
        
    except Exception as e:
        print(f"An error occurred during character translation for frame {frame_index}: {str(e)}")

def create_video(output_dir, video_path, frame_rate=24):
    try:
        # Get list of all frames in sorted order
        frame_paths = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".png")])
        
        # Load the first frame to get the frame dimensions
        first_frame = Image.open(frame_paths[0])
        frame_width, frame_height = first_frame.size
        
        # Initialize the video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec
        video = cv2.VideoWriter(video_path, fourcc, frame_rate, (frame_width, frame_height))
        
        # Write each frame to the video
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            video.write(frame)
        
        video.release()
        print(f"Video saved to: {video_path}")
        
    except Exception as e:
        print(f"An error occurred while creating the video: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Segment character, translate with keyframes, and create parallax video.')
    parser.add_argument('--input_path', default='image.jpg', help='Path to the input image')
    parser.add_argument('--output-dir', default='output', help='Directory to save the output images (default: output)')
    parser.add_argument('--keypoints', type=str, help="List of keypoints in format 'time1:x1,y1 time2:x2,y2 ...'")
    parser.add_argument('--frame-rate', type=int, default=24, help='Frame rate of the video')
    parser.add_argument('--video-path', default='parallax_video.mp4', help='Output path for the final parallax video')
    
    args = parser.parse_args()
    
    # Parse keypoints argument
    keypoints = []
    for keypoint in args.keypoints.split():
        time_pos = keypoint.split(':')
        time = float(time_pos[0])
        x, y = map(int, time_pos[1].split(','))
        keypoints.append((time, (x, y)))
    
    # Step 1: Segment the image into character and background
    segment_image(args.input_path, args.output_dir)
    
    # Step 2: Generate frames by moving the character based on keypoint interpolation
    total_frames = int(keypoints[-1][0] * args.frame_rate)
    for frame_index in range(total_frames):
        position = interpolate_position(keypoints, frame_index, args.frame_rate)
        translate_character(
            os.path.join(args.output_dir, "image_character.png"), 
            os.path.join(args.output_dir, "image_background.png"), 
            args.output_dir, 
            position, 
            frame_index
        )
    
    # Step 3: Compile frames into a video
    create_video(args.output_dir, args.video_path, args.frame_rate)

if __name__ == "__main__":
    main()