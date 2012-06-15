//
//  UIImageHelper.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "UIImageHelper.h"

@implementation UIImage (Helper)

- (void)aspectDrawInRect:(CGRect)rect {
    
    if (self.size.width == self.size.height) {
        [self drawInRect:rect];
        return;
    }
    
    CGSize size = self.size;
    BOOL widthIsGreater = (size.width > size.height);
	float sideFull = (widthIsGreater) ? size.height : size.width;
	CGContextRef ctx = UIGraphicsGetCurrentContext();    
    CGFloat scaleFactor = rect.size.width/sideFull;
    CGFloat transX = widthIsGreater ? -((size.width - sideFull)/2) * scaleFactor : 0;
    CGFloat transY = widthIsGreater ? 0 : -((size.height - sideFull) / 2) * scaleFactor;
	CGContextSaveGState(ctx);
    CGContextTranslateCTM(ctx, transX, transY);
	CGContextScaleCTM(ctx, scaleFactor, scaleFactor);
	[self drawInRect:CGRectMake(0.0f, 0.0f, size.width, size.height)];	
	CGContextRestoreGState(ctx);
    
}

- (UIImage*)aspectScaleToSize:(CGSize)size {
	
	UIGraphicsBeginImageContext(CGSizeMake(size.width, size.height));
    [self aspectDrawInRect:CGRectMake(0.0f, 0.0f, size.width, size.height)];
	UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
	UIGraphicsEndImageContext();
	
	return scaledImage;	
}


@end
