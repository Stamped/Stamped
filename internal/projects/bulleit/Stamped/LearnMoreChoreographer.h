//
//  LearnMoreChoreographer.h
//  Stamped
//
//  Created by Jake Zien on 9/15/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <QuartzCore/QuartzCore.h>

@interface LearnMoreChoreographer : NSObject <UIScrollViewDelegate> {
  @private 
  NSArray* choreoArray_;
//  NSMutableArray* layersArray_;
  
  NSArray* slide0Layers;
  NSArray* slide1Layers;
  NSArray* slide2Layers;
  NSArray* slide3Layers;
  NSArray* slide4Layers;
  CGFloat  offset_;
}

@property (nonatomic, assign) NSArray* slide0Layers;
@property (nonatomic, assign) NSArray* slide1Layers;
@property (nonatomic, assign) NSArray* slide2Layers;
@property (nonatomic, assign) NSArray* slide3Layers;
@property (nonatomic, assign) NSArray* slide4Layers;
/*
- (void)addChoreographyForView:(UIView*)view 
                         range:(NSRange)range 
                      property:(NSString*)property 
                    startValue:(id)sVal 
                      endValue:(id)eVal;

- (void)addChoreographyForLayer:(CALayer*)layer 
                          range:(NSRange)range 
                       property:(NSString*)property 
                     startValue:(id)sVal 
                       endValue:(id)eVal;
*/
@end
