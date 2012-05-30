//
//  QuartzUtils.m
//
//  Created by Devin Doty on 2/23/11.
//  Copyright 2011. All rights reserved.
//

#import "QuartzUtils.h"


@implementation QuartzUtils

void drawGradient(CGColorRef topColor, CGColorRef bottomColor, CGContextRef ctx) {
	
    CGRect rect = CGContextGetClipBoundingBox(ctx);    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 2;
    CGFloat _locations[2] = { 0.0, 1.0 };
    CGFloat _colors[8] = { top[0], top[1], top[2], top[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);

    CGPoint start = CGPointMake(CGRectGetMidX(rect), rect.origin.y);
    CGPoint end = CGPointMake(CGRectGetMidX(rect), rect.size.height);
    
    CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsBeforeStartLocation | kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradient);
	
}

void drawThreePartGradient(CGColorRef topColor, CGColorRef midColor, CGColorRef bottomColor, CGContextRef ctx) {

    CGRect rect = CGContextGetClipBoundingBox(ctx);    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    const CGFloat *mid = CGColorGetComponents(midColor);

    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 3;
    CGFloat _locations[3] = { 0.0, 0.5, 1.0 };
    CGFloat _colors[12] = { top[0], top[1], top[2], top[3], mid[0], mid[1], mid[2], mid[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint start = CGPointMake(CGRectGetMidX(rect), rect.origin.y);
    CGPoint end = CGPointMake(CGRectGetMidX(rect), rect.size.height);
    
    CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsBeforeStartLocation | kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradient);
    
}

void drawFullRadialGradientWithThreeColors(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef midColor2, CGColorRef edgeColor) {
	
    const CGFloat *mid = CGColorGetComponents(midColor);
    const CGFloat *mid2 = CGColorGetComponents(midColor2);
    const CGFloat *edge = CGColorGetComponents(edgeColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 3;
    CGFloat _locations[3] = { 0.0, 0.3, 0.6 };
    CGFloat _colors[12] = { mid[0], mid[1], mid[2], mid[3], mid2[0], mid2[1], mid2[2], mid2[3], edge[0], edge[1], edge[2], edge[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint center = CGPointMake(CGRectGetMidX(rect), CGRectGetMidY(rect));    
    CGContextDrawRadialGradient(ctx, gradient, center, rect.origin.x, center, rect.size.width-100, 0);
    CGGradientRelease(gradient);
	
}

void drawFullRadialGradient(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef edgeColor) {
	
    const CGFloat *mid = CGColorGetComponents(midColor);
    const CGFloat *edge = CGColorGetComponents(edgeColor);

    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 2;
    CGFloat _locations[2] = { 0.0, 0.7 };
    CGFloat _colors[8] = { mid[0], mid[1], mid[2], mid[3], edge[0], edge[1], edge[2], edge[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint center = CGPointMake(CGRectGetMidX(rect), CGRectGetMidY(rect));    
    CGContextDrawRadialGradient(ctx, gradient, center, rect.origin.x, center, rect.size.width-100, 0);
    CGGradientRelease(gradient);
	
}

void drawRadialGradient(CGContextRef ctx, CGRect rect, CGColorRef midColor, CGColorRef edgeColor) {
	
    const CGFloat *bottom = CGColorGetComponents(edgeColor);
    const CGFloat *top = CGColorGetComponents(midColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 2;
    CGFloat _locations[2] = { 0.0, 1.0 };
    CGFloat _colors[8] = { top[0], top[1], top[2], top[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);

    CGPoint center = CGPointMake(CGRectGetMidX(rect), CGRectGetMidY(rect));    
    CGContextDrawRadialGradient(ctx, gradient, center, (rect.size.width/2)-20, center, (rect.size.width/2), 0);
    CGGradientRelease(gradient);
	
}

void drawMidGradient(CGColorRef topColor, CGColorRef midColor1, CGColorRef midColor2, CGColorRef bottomColor, CGContextRef ctx) {
	
    CGRect rect = CGContextGetClipBoundingBox(ctx);   
    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    const CGFloat *mid1 = CGColorGetComponents(midColor1);
    const CGFloat *mid2 = CGColorGetComponents(midColor2);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 4;
    CGFloat _locations[4] = { 0, .5, .5, 1 };
    CGFloat _colors[16] = { top[0], top[1], top[2], top[3], mid1[0], mid1[1], mid1[2], mid1[3], mid2[0], mid2[1], mid2[2], mid2[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
        
    CGPoint gradientStartPoint = CGPointMake(0, rect.origin.y);
	CGPoint gradientEndPoint = CGPointMake(0, rect.size.height+rect.origin.y);
	
	CGContextDrawLinearGradient(ctx, gradient, gradientStartPoint, gradientEndPoint, 0);
    CGGradientRelease(gradient);
	
}

void drawGradientWithStartPoint(CGColorRef topColor, CGColorRef bottomColor, CGFloat startPoint, CGContextRef ctx) {
	
    CGRect rect = CGContextGetClipBoundingBox(ctx);    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 2;
    CGFloat _locations[2] = { 0, 1 };
    CGFloat _colors[8] = { top[0], top[1], top[2], top[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint gradientStartPoint = CGPointMake(0, startPoint);
	CGPoint gradientEndPoint = CGPointMake(0, rect.size.height);
	
	CGContextDrawLinearGradient(ctx, gradient, gradientStartPoint, gradientEndPoint, 0);
    CGGradientRelease(gradient);
	
}

void drawGradientWithLine(CGColorRef topColor, CGColorRef bottomColor, CGColorRef lineColor, CGContextRef ctx) {
    
    CGRect rect = CGContextGetClipBoundingBox(ctx);
    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    const CGFloat *line = CGColorGetComponents(lineColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 3;
    CGFloat _locations[3] = { 0.0, 0.99, 1.0 };
    CGFloat _colors[12] = { top[0], top[1], top[2], top[3], bottom[0], bottom[1], bottom[2], bottom[3], line[0], line[1], line[2], line[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint start = CGPointMake(CGRectGetMidX(rect), rect.origin.y);
    CGPoint end = CGPointMake(CGRectGetMidX(rect), rect.size.height);
    
    CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsBeforeStartLocation | kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradient);
    
}

void aspectDrawImageInRect(CGContextRef ctx, CGImageRef cgImage, CGRect rect) {
    
    size_t width = CGImageGetWidth(cgImage);
    size_t height = CGImageGetHeight(cgImage);
    
    CGSize sourceSize = CGSizeMake(width, height);
	CGSize targetSize = rect.size;
	BOOL clipWidth = NO;
	
	if(targetSize.width > targetSize.height) {
		if(sourceSize.width > sourceSize.height) {
			if((sourceSize.height / sourceSize.width) >= (targetSize.height / targetSize.width)) {
				clipWidth = NO;
			} else {
				clipWidth = YES;
			}
		} else {
			clipWidth = NO;
		}
	} else {
		if(sourceSize.height > sourceSize.width) {
			if((sourceSize.width  / sourceSize.height) >= (targetSize.width / targetSize.height)) {
				clipWidth = YES;
			} else {
				clipWidth = NO;
			}
		} else {
			clipWidth = YES;
		}
	}
	
	CGContextClipToRect(ctx, rect);
	CGRect rectToDraw = rect;
	
	if(clipWidth) {
		CGSize drawSize = targetSize;
		rectToDraw.size.width = drawSize.width = (sourceSize.width * targetSize.height) / sourceSize.height;
		rectToDraw.origin.x -= floorf((drawSize.width - targetSize.width) / 2);
	} else {
		CGSize drawSize = targetSize;
		rectToDraw.size.height = drawSize.height = (sourceSize.height * targetSize.width) / sourceSize.width;
        rectToDraw.origin.y -= floorf((drawSize.height - targetSize.height) / 2);
	}
    
    CGContextDrawImage(ctx, rectToDraw, cgImage);

}

void drawStampGradient(CGColorRef topColor, CGColorRef bottomColor, CGContextRef ctx) {
	
    CGRect rect = CGContextGetClipBoundingBox(ctx);    
    const CGFloat *bottom = CGColorGetComponents(bottomColor);
    const CGFloat *top = CGColorGetComponents(topColor);
    
    CGColorSpaceRef _rgb = CGColorSpaceCreateDeviceRGB();
    size_t _numLocations = 2;
    CGFloat _locations[2] = { 0.0, 1.0 };
    CGFloat _colors[8] = { top[0], top[1], top[2], top[3], bottom[0], bottom[1], bottom[2], bottom[3] };
    CGGradientRef gradient = CGGradientCreateWithColorComponents(_rgb, _colors, _locations, _numLocations);
    CGColorSpaceRelease(_rgb);
    
    CGPoint start = CGPointMake(0.0f, rect.size.height);
    CGPoint end = CGPointMake(rect.size.width, 0.0f);
    
    CGContextDrawLinearGradient(ctx, gradient, start, end, kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradient);
	
}

@end
