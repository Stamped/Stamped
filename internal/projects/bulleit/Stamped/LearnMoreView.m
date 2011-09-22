//
//  LearnMoreView.m
//  Stamped
//
//  Created by Jake Zien on 9/14/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "LearnMoreView.h"
#import "LearnMoreChoreographer.h"

@interface LearnMoreView ()

- (void)setupSlide:(UIImageView*)imageView;
- (void)setupLayersForUIImageView:(UIImageView*)imageView;


@end

static CGFloat const kSlide0X = 0;
static CGFloat const kSlide1X = 380;
static CGFloat const kSlide2X = 760;
static CGFloat const kSlide3X = 1140;
static CGFloat const kSlide4X = 1520;
static CGFloat const kSlideWidth = 380;

@implementation LearnMoreView


@synthesize scrollView;
@synthesize choreographer = choreographer_;


- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) { }
  return self;
}

- (void)dealloc {
  self.scrollView.delegate = nil;
  [choreographer_ release];
}

- (void)awakeFromNib {
  
  choreographer_ = [[LearnMoreChoreographer alloc] init];
  self.scrollView.delegate = self.choreographer;
  
  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"],
                       [UIImage imageNamed:@"learnmore_01"],
                       [UIImage imageNamed:@"learnmore_02_stamp"],
                       [UIImage imageNamed:@"learnmore_03"],
                       [UIImage imageNamed:@"learnmore_04_stamps"], nil];
  
  for (NSUInteger i = 0; i < bgImages.count; ++i) {
    UIImageView* subview = [[UIImageView alloc] initWithImage:[bgImages objectAtIndex:i]];
    
    CGRect frame = self.scrollView.frame;
    frame.origin.x = CGRectGetWidth(frame) * i;
    subview.frame = frame;
    subview.clipsToBounds = NO;
    subview.contentMode = UIViewContentModeCenter;
    
    [self setupLayersForUIImageView:subview];
    
    [self.scrollView addSubview:subview];
    
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(CGRectGetWidth(self.scrollView.frame) * bgImages.count,
                                           CGRectGetHeight(self.scrollView.frame)); 
  
  
}



- (void)setupLayersForUIImageView:(UIImageView*)imageView
{
  if (imageView.image == [UIImage imageNamed:@"learnmore_01"]) {
  
    // Second slide (5 stars)    
    UIImage* greyStarImg   = [UIImage imageNamed:@"learnmore_star_grey"];
    UIImage* yellowStarImg = [UIImage imageNamed:@"learnmore_star_yellow"];

    for (NSUInteger i = 0; i < 5; ++i) {
      CALayer* greyStar   = [CALayer layer];
      CALayer* yellowStar = [CALayer layer];
      greyStar.contents   = (id)greyStarImg.CGImage;
      yellowStar.contents = (id)yellowStarImg.CGImage;
      CGRect frame = CGRectMake(90 + (i * greyStarImg.size.width), 169, greyStarImg.size.width, greyStarImg.size.height);
      greyStar.frame   = frame;
      yellowStar.frame = frame;
      yellowStar.opacity = 0.0;
      
      // Add Animations 
      NSMutableArray*   choreoArray = [NSMutableArray array];
      
      NSMutableDictionary* animDict = [NSMutableDictionary dictionary];
      
      // // Fade in
      NSRange range = NSMakeRange(260.0 + (20*i), 30.0);
      [animDict setObject:@"opacity"                     forKey:@"property"];
      [animDict setValue:[NSNumber numberWithFloat:0.0]  forKey:@"startValue"];
      [animDict setValue:[NSNumber numberWithFloat:1.0]  forKey:@"endValue"];
      [animDict setValue:[NSValue valueWithRange:range]  forKey:@"range"];
      [choreoArray addObject:animDict];
      
      animDict = [NSMutableDictionary dictionary];
      range = NSMakeRange(0, range.location-1);
      [animDict setObject:@"opacity"                     forKey:@"property"];
      [animDict setValue:[NSNumber numberWithFloat:0.0]  forKey:@"startValue"];
      [animDict setValue:[NSNumber numberWithFloat:0.0]  forKey:@"endValue"];
      [animDict setValue:[NSValue valueWithRange:range]  forKey:@"range"];
      [choreoArray addObject:animDict];
      
      animDict = [NSMutableDictionary dictionary];
      range = NSMakeRange(range.length+32, 100.0);
      NSLog(@"%d %d", range.location, range.location+range.length);
      [animDict setObject:@"opacity"                     forKey:@"property"];
      [animDict setValue:[NSNumber numberWithFloat:1.0]  forKey:@"startValue"];
      [animDict setValue:[NSNumber numberWithFloat:1.0]  forKey:@"endValue"];
      [animDict setValue:[NSValue valueWithRange:range]  forKey:@"range"];
      [choreoArray addObject:animDict];
      
/*      
      // // Jump
      range = NSMakeRange(400.0 + (30*i), 40.0);
      CGPoint  startPt = CGPointMake(frame.origin.x, frame.origin.y);
      CGPoint    endPt = CGPointMake(440.0, frame.origin.y);
      CGSize      size = CGSizeMake(frame.size.width, frame.size.height);
      CGRect startRect = CGRectMake(startPt.x, startPt.y, size.width, size.height);
      CGRect   endRect = CGRectMake(endPt.x, endPt.y, size.width, size.height);
      
      animDict = [NSMutableDictionary dictionary];
      [animDict setObject:@"jump"                            forKey:@"property"];
      [animDict setValue:[NSValue valueWithCGRect:startRect] forKey:@"startValue"];
      [animDict setValue:[NSValue valueWithCGRect:endRect]   forKey:@"endValue"];
      [animDict setValue:[NSValue valueWithRange:range]      forKey:@"range"];
      [choreoArray addObject:animDict];
      
      animDict = [NSMutableDictionary dictionary];
      range = NSMakeRange(300, 81);
      [animDict setObject:@"frame"                       forKey:@"property"];
      [animDict setValue:[NSValue valueWithCGRect:frame] forKey:@"startValue"];
      [animDict setValue:[NSValue valueWithCGRect:frame] forKey:@"endValue"];
      [animDict setValue:[NSValue valueWithRange:range]  forKey:@"range"];
      [choreoArray addObject:animDict];
      
//      animDict = [NSMutableDictionary dictionary];
//      range = NSMakeRange(range.length + 30.0, 200.0);
//      [animDict setObject:@"frame"                       forKey:@"property"];
//      [animDict setValue:[NSNumber numberWithFloat:1.0]  forKey:@"startValue"];
//      [animDict setValue:[NSNumber numberWithFloat:1.0]  forKey:@"endValue"];
//      [animDict setValue:[NSValue valueWithRange:range]  forKey:@"range"];
//      [choreoArray addObject:animDict];
*/
      [yellowStar setValue:choreoArray forKey:@"choreoArray"];

      [imageView.layer addSublayer:greyStar];
      [imageView.layer addSublayer:yellowStar];
    }
    
    self.choreographer.slide1Layers = imageView.layer.sublayers;
  }
}


- (void)setupSlide:(UIView*)view {
  /*
  UIImage* starImg = [UIImage imageNamed:@"learnmore_star"];
  
  for (NSUInteger i = 0; i < 5; ++i) {
    UIImageView* starView = [[UIImageView alloc] initWithImage:starImg];
    CGRect frame = CGRectMake(26 + (i * starImg.size.width - 12), 95, starImg.size.width, starImg.size.height);
    starView.frame = frame;
    starView.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.5];
    [view addSubview:starView];

    if (i==2)
    [self.choreographer addChoreographyForView:starView
                                         range:NSMakeRange(1, 419)
                                      property:@"frame.origin.y"
                                    startValue:[NSNumber numberWithInt:4]
                                      endValue:[NSNumber numberWithInt:10]];
    
    [starView release];
   
  } */ 
}


@end