//
//  QuartzUtils.h
//
//  Created by Devin Doty on 2/23/11.
//  Copyright 2011. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface QuartzUtils : NSObject {

}

/*
 * Draw linear gradient
 */
void drawGradient(CGColorRef color1, CGColorRef color2, CGContextRef context);
void drawThreePartGradient(CGColorRef topColor, CGColorRef midColor, CGColorRef bottomColor, CGContextRef ctx);

/*
 * Draw radial gradient from center
 */
void drawRadialGradient(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef edgeColor);
void drawFullRadialGradient(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef edgeColor);
void drawFullRadialGradientWithThreeColors(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef midColor2, CGColorRef edgeColor);

/*
 * Linear Gradient with single line at the end
 */
void drawGradientWithLine(CGColorRef topColor, CGColorRef bottomColor, CGColorRef lineColor, CGContextRef ctx);
void drawGradientWithStartPoint(CGColorRef topColor, CGColorRef bottomColor, CGFloat startPoint, CGContextRef ctx);
void drawMidGradient(CGColorRef topColor, CGColorRef midColor1, CGColorRef midColor2, CGColorRef bottomColor, CGContextRef ctx);

/*
 * Create color from image pattern
 */
CGColorRef CreatePatternColor(CGImageRef image);
void aspectDrawImageInRect(CGContextRef ctx, CGImageRef cgImage, CGRect rect);


@end
