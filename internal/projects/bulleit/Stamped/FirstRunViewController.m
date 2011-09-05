//
//  LearnMoreViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "LearnMoreViewController.h"

@implementation LearnMoreViewController

@synthesize scrollView = scrollView_;
@synthesize bottomView = bottomView_;
@synthesize animView = animView_;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}


#pragma mark - View lifecycle

- (void)viewDidLoad
{
  [super viewDidLoad];

  [self setupBottomView];
//  [self createContentArray];

  NSArray* bgImages = [NSArray arrayWithObjects:[UIImage imageNamed:@"learnmore_00"], [UIImage imageNamed:@"learnmore_01"], [UIImage imageNamed:@"learnmore_02"], [UIImage imageNamed:@"learnmore_03"],[UIImage imageNamed:@"learnmore_04"], nil];
  
  for (int i = 0; i < bgImages.count; i++) {
    CGRect frame;
    frame.origin.x = self.scrollView.frame.size.width * i;
    frame.origin.y = 0;
    frame.size = self.scrollView.frame.size;
    
    UIImageView *subview = [[UIImageView alloc] initWithFrame:frame];
    subview.image = [bgImages objectAtIndex:i];
    subview.clipsToBounds = YES;
    subview.contentMode = UIViewContentModeRight;
    
    if (i==1) [self setupSlide:subview];
    
    [self.scrollView addSubview:subview];
    [subview release];
  }
  
  self.scrollView.contentSize = CGSizeMake(self.scrollView.frame.size.width * bgImages.count, self.scrollView.frame.size.height);
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}



#pragma mark - Setup Views

- (void)setupBottomView
{
  CAGradientLayer* bottomGradient = [[CAGradientLayer alloc] init];
  bottomGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.88 alpha:1.0].CGColor, nil];
  bottomGradient.frame = bottomView_.bounds;
  
  
  [bottomView_.layer insertSublayer:bottomGradient atIndex:0];
  [bottomGradient release];
}


- (void)setupSlide:(UIImageView*)imageView
{
  UIImage* starImg = [UIImage imageNamed:@"learnmore_star"];

   
  for (int i=0; i<5; i++)
  {    
    CGRect frame;
    frame.origin.x = 26 + (i*starImg.size.width-12); //to get the spacing right.
    frame.origin.y = 95;
    frame.size.width = starImg.size.width;
    frame.size.height = starImg.size.height;
    
    UIImageView* starView = [[UIImageView alloc] initWithImage:starImg];;
    starView.frame = frame;
    starView.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.5];;
    
    [imageView addSubview:starView];
    [starView release];

  }
}

#pragma mark - ScrollView Animation functions
- (void)scrollViewDidScroll:(UIScrollView *)sender
{
//  NSLog(@"%f", sender.contentOffset.x);
  
}




#pragma mark - Utility/Helper functions
- (UIImage*)maskImage:(UIImage *)image
              withMask:(UIImage *)maskImage
{
  CGImageRef imageRef = image.CGImage;
  CGImageRef maskRef = maskImage.CGImage;
  CGImageRef mask = CGImageMaskCreate(CGImageGetWidth(maskRef),
                                      CGImageGetHeight(maskRef),
                                      CGImageGetBitsPerComponent(maskRef),
                                      CGImageGetBitsPerPixel(maskRef),
                                      CGImageGetBytesPerRow(maskRef),
                                      CGImageGetDataProvider(maskRef),
                                      NULL, // decode should be NULL
                                      FALSE // shouldInterpolate
                                      );
  CGImageRef masked = CGImageCreateWithMask(imageRef, mask);
  CGImageRelease(mask);
  UIImage *maskedImage = [UIImage imageWithCGImage:masked];
  CGImageRelease(masked);
  return maskedImage;
}


@end
