from rembg import remove
from PIL import Image
import numpy as np
import os
import argparse

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

# TODO: Implement translation logic to move the segmented character based on input vector
def translate_character(character_path, output_dir, translation_vector):
    # Use translation_vector to move character image position relative to background
    pass

# TODO: Implement background generation to fill areas based on parallax effect
def generate_background(background_path, mask_path, output_dir):
    # Use generative model to fill background, especially for parallax effect
    pass

# TODO: Compile images into a parallax video sequence
def create_video(output_dir, video_path, frame_rate=24):
    # Compile individual frames into a video
    pass

def main():
    parser = argparse.ArgumentParser(description='Segment character, translate, generate background, and create parallax video.')
    parser.add_argument('--input_path', default='image.jpg', help='Path to the input image')
    parser.add_argument('--output-dir', default='output', help='Directory to save the output images (default: output)')
    parser.add_argument('--translation-vector', type=str, default="0,0", help="Translation vector as x,y for character movement")
    parser.add_argument('--video-path', default='parallax_video.mp4', help='Output path for the final parallax video')
    
    args = parser.parse_args()
    translation_vector = tuple(map(int, args.translation_vector.split(',')))

    # Step 1: Segment the image into character and background
    segment_image(args.input_path, args.output_dir)
    
    # Step 2: Move the character based on translation vector
    translate_character(os.path.join(args.output_dir, "character.png"), args.output_dir, translation_vector)
    
    # Step 3: Generate background to fill empty areas
    generate_background(os.path.join(args.output_dir, "background.png"), os.path.join(args.output_dir, "mask.png"), args.output_dir)
    
    # Step 4: Compile frames into a video
    create_video(args.output_dir, args.video_path)

if __name__ == "__main__":
    main()