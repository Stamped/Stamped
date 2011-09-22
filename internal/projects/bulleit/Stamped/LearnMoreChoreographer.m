//
//  LearnMoreChoreographer.m
//  Stamped
//
//  Created by Jake Zien on 9/15/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//
//
// This class handles the animation of the Learn More section of the app.
// 
// It owns choreoArray, an NSArray that stores four NSMutableArrays, one for
// each of the four transitions between Learn More slides. These store NSMutableDictionaries 
// that each contain a reference to a view and an NSArray that stores the animations for that view.
// Animations (choreography) are stored as NSDictionaries. 
// 
// -(void)performForOffset: does the actual animation. It determines which slides
// are transitioning, pulls the relelvant animations, and performs them, 
// interpolating between the values and setting the appropriate properties of
// the appropriate view.

#import "LearnMoreChoreographer.h"


@interface LearnMoreChoreographer ()

//- (NSUInteger)sceneForRange:(NSRange)range;
- (NSUInteger)sceneforOffset;
- (void)performForOffset:(CGFloat)offset;
- (void)applyAnimation:(NSDictionary*)animDict toLayer:(CALayer*)layer;
//- (BOOL)scene:(NSUInteger)sceneNumber includesView:(UIView*)view;




@end



static CGFloat const kSlide0X = 0;
static CGFloat const kSlide1X = 420;
static CGFloat const kSlide2X = 840;
static CGFloat const kSlide3X = 1260;
static CGFloat const kSlide4X = 1680;

static inline float lerpf(float a, float b, float t)
{
  return a + ((b - a) * t);
}

static inline CGPoint lerpPoint(CGPoint a, CGPoint b, float t)
{
  return CGPointMake(lerpf(a.x, b.x, t), lerpf(a.y, b.y, t));
}

static inline CGSize lerpSize(CGSize a, CGSize b, float t)
{
  return CGSizeMake(lerpf(a.width, b.width, t), lerpf(a.height, b.height, t));
}



@implementation LearnMoreChoreographer

@synthesize slide0Layers = slide0Layers_;
@synthesize slide1Layers = slide1Layers_;
@synthesize slide2Layers = slide2Layers_;
@synthesize slide3Layers = slide3Layers_;
@synthesize slide4Layers = slide4Layers_;

- (id)init {
    self = [super init];
    if (self) {      
    }
    
  
    return self;
}

- (void)dealloc {
  [choreoArray_ release];
  [slide0Layers_ release];
  [slide1Layers_ release];
  [slide2Layers_ release];
  [slide3Layers_ release];
  [slide4Layers_ release];
}


- (NSInteger)sceneForOffset {
  if (offset_ >= kSlide3X) return 3;
  if (offset_ >= kSlide2X) return 2;
  if (offset_ >= kSlide1X) return 1;
  
  return 0;
}




- (void)performForOffset:(CGFloat)offset {
  
  offset_ = offset;
//  NSUInteger scene = [self sceneForOffset];
 
  /*
  NSArray* lastSlideLayers;
  NSArray* nextSlideLayers;
  
  if (scene == 0)      {lastSlideLayers = self.slide0Layers; nextSlideLayers = self.slide1Layers;}
  else if (scene == 1) {lastSlideLayers = self.slide1Layers; nextSlideLayers = self.slide2Layers;}
  else if (scene == 2) {lastSlideLayers = self.slide2Layers; nextSlideLayers = self.slide3Layers;}
  else if (scene == 3) {lastSlideLayers = self.slide3Layers; nextSlideLayers = self.slide4Layers;}
  */
   
//  if (!lastSlideLayers) // || !nextSlideLayers)
//    return;
  
   
  for (CALayer* layer in self.slide1Layers) {
    NSArray* choreoArray = [layer valueForKey:@"choreoArray"];
    if (!choreoArray || choreoArray.count == 0 ) continue;
    
    for (NSDictionary* animDict in choreoArray) {
      NSRange range = ((NSValue*)[animDict valueForKey:@"range"]).rangeValue;
      if (NSLocationInRange((NSUInteger)offset_, range))
        [self applyAnimation:animDict toLayer:layer];
    }
  }
}
  



- (void)applyAnimation:(NSDictionary *)animDict toLayer:(CALayer *)layer {
  
  NSString* property = [animDict valueForKey:@"property"];
  
  // calculate t value for interpolation
  NSRange range = ((NSValue*)[animDict valueForKey:@"range"]).rangeValue;
  CGFloat t = (offset_-range.location) / lerpf(0, range.length, 1.0);
  
  if ([property isEqualToString:@"opacity"])
  {
    CGFloat startOpacity = ((NSNumber*)[animDict valueForKey:@"startValue"]).floatValue;
    CGFloat endOpacity   = ((NSNumber*)[animDict valueForKey:@"endValue"]).floatValue;
    
    [CATransaction begin]; 
    [CATransaction setValue: (id) kCFBooleanTrue forKey: kCATransactionDisableActions];
      if (startOpacity == endOpacity) layer.opacity = startOpacity;
      else layer.opacity = lerpf(startOpacity, endOpacity, t);
    [CATransaction commit];
    //    NSLog(@"%f", layer.opacity);
  }
  
  if ([property isEqualToString:@"frame"])
  {
    CGRect startFrame = ((NSValue*)[animDict valueForKey:@"startValue"]).CGRectValue;
    CGRect   endFrame = ((NSValue*)[animDict valueForKey:@"endValue"]).CGRectValue;
    
    CGPoint origin = lerpPoint(startFrame.origin, endFrame.origin, t);
    CGSize    size = lerpSize(startFrame.size, endFrame.size, t);
    
    CGRect newFrame = CGRectMake(origin.x, origin.y, size.width, size.height);

//    [CATransaction begin]; 
//    [CATransaction setValue: (id) kCFBooleanTrue forKey: kCATransactionDisableActions];
      layer.frame = newFrame;
//    [CATransaction commit];
  }
  

  if ([property isEqualToString:@"jump"])
  {
    CGRect startFrame = ((NSValue*)[animDict valueForKey:@"startValue"]).CGRectValue;
    CGRect   endFrame = ((NSValue*)[animDict valueForKey:@"endValue"]).CGRectValue;
    
    CGPoint origin = lerpPoint(startFrame.origin, endFrame.origin, t);
    CGSize    size = lerpSize(startFrame.size, endFrame.size, t);

    CGFloat upVelocity = 0.0;
    if (t <= 0.33)
      upVelocity = lerpf(1, 100, fmax(t*3, 1.0));
//    if (t > 0.17)
//      upVelocity = lerpf(100, 0, fmax(t*6, 1.0));
//    CGFloat downVelocity = lerpf(0, -100, fmax(t*2, 1.0));
    origin.y -= (upVelocity - 10.0);
    
    NSLog(@"%f", upVelocity - 10.0);
    
//    [CATransaction begin]; 
//    [CATransaction setValue: (id) kCFBooleanTrue forKey: kCATransactionDisableActions];
      CGRect newFrame = CGRectMake(origin.x, origin.y, size.width, size.height);
      layer.frame = newFrame;
//    [CATransaction commit];
  }

  
}
  

  
#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView *)theScrollView
{
//  NSLog(@"%f", theScrollView.contentOffset.x);
  [self performForOffset:theScrollView.contentOffset.x];
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)theScrollView
{
  [self performForOffset:theScrollView.contentOffset.x];
//  NSLog(@"%f", theScrollView.contentOffset.x);
}

@end



/*  
 NSUInteger sceneNumber = [self sceneForOffset:offset];
 NSArray*    sceneArray = [choreoArray_ objectAtIndex:sceneNumber];
 
 for (NSDictionary* viewDict in sceneArray)
 {
 NSArray* animsArray = [viewDict valueForKey:@"animsArray"];
 
 for (NSDictionary* animDict in animsArray)
 {
 NSRange range = ((NSValue*)[animDict valueForKey:@"range"]).rangeValue;
 if (NSLocationInRange(offset, range))
 NSLog(@"in range");
 
 }
 }
 */  

/*
 - (void)addChoreographyForView:(UIView*)view 
 range:(NSRange)range 
 property:(NSString*)property
 startValue:(id)sVal
 endValue:(id)eVal  {
 
 // Create a dict to store the animation properties.
 NSMutableDictionary* choreography = [NSMutableDictionary dictionary];
 
 [choreography setValue:sVal      forKey:@"sVal"];
 [choreography setValue:eVal      forKey:@"eVal"];
 [choreography setObject:property forKey:@"property"];
 [choreography setValue:[NSValue valueWithRange:range] forKey:@"range"];
 
 
 
 NSUInteger     sceneNumber = [self sceneForRange:range];
 NSMutableArray* sceneArray = [choreoArray_ objectAtIndex:sceneNumber];
 NSDictionary*     viewDict = [self viewDictForView:view scene:sceneNumber];
 
 // If this view isn't part of the scene yet, add it.
 if (!viewDict) {
 NSMutableArray* animsArray = [NSMutableArray array];
 NSMutableDictionary* newDict = [NSMutableDictionary dictionary];
 [newDict setObject:view forKey:@"view"];
 
 [newDict setObject:animsArray forKey:@"animsArray"];
 
 [sceneArray addObject:newDict];
 viewDict = newDict;
 }
 
 NSMutableArray* animsArray = [viewDict objectForKey:@"animsArray"];
 [animsArray addObject:(id)choreography];
 }
 
 
 - (void)addChoreographyForLayer:(CALayer *)layer 
 range:(NSRange)range 
 property:(NSString *)property 
 startValue:(id)sVal
 endValue:(id)eVal {
 
 // Create a dict to store the animation properties.
 NSMutableDictionary* choreography = [NSMutableDictionary dictionary];
 
 [choreography setValue:sVal      forKey:@"sVal"];
 [choreography setValue:eVal      forKey:@"eVal"];
 [choreography setObject:property forKey:@"property"];
 [choreography setValue:[NSValue valueWithRange:range] forKey:@"range"];
 
 
 // If the layer isn't in layersArray_, add it.
 NSUInteger index = [layersArray_ indexOfObject:layer];
 if (index == NSNotFound) {
 [layersArray_ addObject:layer];
 index = layersArray_.count - 1;
 }
 
 
 
 }
 */

//- (NSDictionary*)viewDictForView:(UIView*)view scene:(NSUInteger)sceneNumber {
//  NSArray* sceneArray = [choreoArray_ objectAtIndex:sceneNumber];
//
//  if (sceneArray.count > 0)
//    for (NSDictionary* viewDict in sceneArray) 
//      if ([viewDict objectForKey:@"view"] == view)
//        return viewDict;
//  
//  return nil;
//}

