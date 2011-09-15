//
//  LearnMoreChoreographer.m
//  Stamped
//
//  Created by Jake Zien on 9/15/11.
//  Copyright 2011 RISD. All rights reserved.
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

- (NSUInteger)sceneForRange:(NSRange)range;
- (NSUInteger)sceneforOffset:(CGFloat)offset;
- (void)performForOffset:(CGFloat)offset;
- (BOOL)scene:(NSUInteger)sceneNumber includesView:(UIView*)view;

@end



static CGFloat const kSlide0X = 0;
static CGFloat const kSlide1X = 420;
static CGFloat const kSlide2X = 840;
static CGFloat const kSlide3X = 1260;
static CGFloat const kSlide4X = 1680;


@implementation LearnMoreChoreographer

- (id)init
{
    self = [super init];
    if (self) {
      choreoArray_ = [NSMutableArray arrayWithObjects:(id)[NSMutableArray arrayWithCapacity:50],
                                                     (id)[NSMutableArray arrayWithCapacity:50],
                                                     (id)[NSMutableArray arrayWithCapacity:50],
                                                     (id)[NSMutableArray arrayWithCapacity:50], nil];
      [choreoArray_ retain];
      
    }
    
  
    return self;
}

- (NSUInteger)sceneForRange:(NSRange)range
{
//  NSLog(@"%@", choreoArray_);

  if (range.location >= kSlide3X) return 3;
  if (range.location >= kSlide2X) return 2;
  if (range.location >= kSlide1X) return 1;
  
  return 0;
}

- (NSInteger)sceneForOffset:(CGFloat)offset;
{
  if (offset >= kSlide3X) return 3;
  if (offset >= kSlide2X) return 2;
  if (offset >= kSlide1X) return 1;
  
  return 0;
}

- (NSDictionary*)viewDictForView:(UIView*)view scene:(NSUInteger)sceneNumber
{
  NSArray* sceneArray = [choreoArray_ objectAtIndex:sceneNumber];

  if (sceneArray.count > 0)
    for (NSDictionary* viewDict in sceneArray) 
      if ([viewDict objectForKey:@"view"] == view)
        return viewDict;
  
  return nil;
}


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



- (void)performForOffset:(CGFloat)offset {
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
  
}
  

  
#pragma mark - UIScrollView delegate methods

- (void)scrollViewDidScroll:(UIScrollView *)theScrollView
{
  [self performForOffset:theScrollView.contentOffset.x];
}



@end
