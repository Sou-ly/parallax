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

def main():
    parser = argparse.ArgumentParser(description='Segment a character from an image and save both character and background.')
    parser.add_argument('--input_path', default='image.jpg', help='Path to the input image')
    parser.add_argument('--output-dir', default='output',
                        help='Directory to save the output images (default: output)')
    
    args = parser.parse_args()
    
    segment_image(args.input_path, args.output_dir)

if __name__ == "__main__":
    main()