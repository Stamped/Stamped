//
//  UIImageHelper.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "UIImageHelper.h"

#import "Util.h"

@implementation UIImage (Helper)

- (void)aspectDrawInRect:(CGRect)rect {
    CGSize size = self.size;
    CGFloat width = MIN(size.width, rect.size.width);
    BOOL widthIsGreater = (size.width > size.height);
	float sideFull = (widthIsGreater) ? size.height : size.width;
	CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextSetFillColorWithColor(ctx, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:1.0f].CGColor);
    CGContextFillRect(ctx, rect);
    CGFloat scaleFactor = width/sideFull;
    CGFloat transX = widthIsGreater ? -((size.width - sideFull)/2) * scaleFactor : 0;
    CGFloat transY = widthIsGreater ? 0 : -((size.height - sideFull) / 2) * scaleFactor;
	CGContextSaveGState(ctx);
    CGContextTranslateCTM(ctx, transX, transY);
	CGContextScaleCTM(ctx, scaleFactor, scaleFactor);
	[self drawInRect:CGRectMake(0.0f, 0.0f, size.width, size.height)];	
	CGContextRestoreGState(ctx);
    
}

- (UIImage*)aspectScaleToSize:(CGSize)bounds {
	CGRect rect = [Util centeredAndBounded:self.size inFrame:CGRectMake(0, 0, bounds.width, bounds.height)];
    CGSize size = rect.size;
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(NULL, size.width, size.height, 8, 0, colorSpace, kCGImageAlphaPremultipliedLast);
    CGContextClearRect(context, CGRectMake(0, 0, size.width, size.height));
    
    if(self.imageOrientation == UIImageOrientationRight)
    {
        CGContextRotateCTM(context, -M_PI_2);
        CGContextTranslateCTM(context, -size.height, 0.0f);
        CGContextDrawImage(context, CGRectMake(0, 0, size.height, size.width), self.CGImage);
    }
    else
        CGContextDrawImage(context, CGRectMake(0, 0, size.width, size.height), self.CGImage);
    
    CGImageRef scaledImage=CGBitmapContextCreateImage(context);
    
    CGColorSpaceRelease(colorSpace);
    CGContextRelease(context);
    
    UIImage *image = [UIImage imageWithCGImage: scaledImage];
    
    CGImageRelease(scaledImage);
    
    return image;
}


@end
