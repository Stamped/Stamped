//
//  STHeaderViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STHeaderViewFactory.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import <CoreText/CoreText.h>
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import <CoreLocation/CoreLocation.h>
#import <MapKit/MapKit.h>
#import "STPlaceAnnotation.h"
#import "STActionManager.h"
#import "STSimpleAction.h"
#import "ShowImageViewController.h"

static const CGFloat _standardLatLongSpan = 600.0f / 111000.0f;

@interface STHeaderViewFactory ()

@property (nonatomic, readonly, retain) NSString* style;

@end

/*
 
 Sample image push from old eDetail
 
 - (void)imageViewTapped {
 ShowImageViewController* controller = [[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil];
 if (self.imageView.image) {
 controller.image = self.imageView.image;
 } else if (detailedEntity_.image && detailedEntity_.image.length > 0) {
 controller.imageURL = detailedEntity_.image;
 } else {
 [controller release];
 return;
 }
 [self.navigationController pushViewController:controller animated:YES];
 [controller release];
 }
 
 - (void)STImageView:(STImageView*)imageView didLoadImage:(UIImage*)image {
 // Default does nothing. Override in subclasses.
 }
 */

@implementation STHeaderViewFactory

@synthesize style = _style;

- (id)initWithStyle:(NSString*)style {
  self = [super init];
  if (self) {
    _style = [style retain];
  }
  return self;
}

- (void)dealloc
{
  [_style release];
  [super dealloc];
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)entity
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  UIView* view = nil;
  if (entity) {
    CGFloat padding_h = 15;
    CGFloat maxWidth = 200;
    CGFloat maxImageWidth = 320 - (maxWidth + 3 * padding_h);
    if ([self.style isEqualToString:@"StampDetail"]) {
      maxImageWidth = 200;
    }
    NSString* imagePath = nil;
    if (entity.images && [entity.images count] > 0) {
      id<STImageList> imageList = [entity.images objectAtIndex:0];
      if (imageList.sizes.count > 0) {
        id<STImage> firstImage = [imageList.sizes objectAtIndex:0];
        imagePath = firstImage.image;
      }
    }
    UIView* imageView = nil;
    CGRect imageFrame = CGRectZero;
    if (imagePath) {
      imageView = [Util imageViewWithURL:[NSURL URLWithString:imagePath] andFrame:CGRectNull];
      imageFrame = imageView.frame;
      if (imageFrame.size.width > maxImageWidth) {
        CGFloat factor = maxImageWidth / imageFrame.size.width;
        imageFrame.size.width = maxImageWidth;
        imageFrame.size.height *= factor;
      }
    }
    CGFloat height = imageFrame.size.height;
    CGFloat padding = 10;
    CGFloat paddingBetween = 0;
    UIView* titleView = nil;
    UIView* captionView = nil;
    if (![self.style isEqualToString:@"StampDetail"]) {
      UIFont* titleFont = [UIFont stampedTitleFontWithSize:30];
      UIFont* captionFont = [UIFont stampedFontWithSize:12];
      
      titleView = [Util viewWithText:entity.title
                                font:titleFont
                               color:[UIColor stampedDarkGrayColor]
                                mode:UILineBreakModeWordWrap
                          andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
      
      captionView = [Util viewWithText:entity.caption ? entity.caption : entity.subtitle
                                  font:captionFont
                                 color:[UIColor stampedGrayColor]
                                  mode:UILineBreakModeWordWrap
                            andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
      CGFloat combinedHeight = titleView.frame.size.height + paddingBetween + captionView.frame.size.height;
      height = MAX(combinedHeight, height);
      
      CGFloat offset = (height - combinedHeight) / 2 + padding;
      
      
      CGRect titleFrame = titleView.frame;
      titleFrame.origin = CGPointMake(padding_h, offset);
      titleView.frame = titleFrame;
      CGRect captionFrame = captionView.frame;
      captionFrame.origin = CGPointMake(padding_h, CGRectGetMaxY(titleFrame) + paddingBetween);
      captionView.frame = captionFrame;
    }
    if (imageView) {
      CGFloat imageOffset = (height - imageFrame.size.height) / 2 + padding;
      imageFrame.origin = CGPointMake(320 - (imageFrame.size.width + padding_h), imageOffset);
      imageView.frame = imageFrame;
      imageView.layer.shadowColor = [UIColor blackColor].CGColor;
      imageView.layer.shadowOpacity = .2;
      imageView.layer.shadowRadius = 2.0;
      imageView.layer.shadowOffset = CGSizeMake(0, 2);
      imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;
    }
    
    CGRect frame = CGRectMake(0, 0, 320, 0);
    frame.size.height = height + 2 * padding;
    
    if (imageView && !(titleView || captionView)) {
      imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:frame];
    }
    
    view = [[UIView alloc] initWithFrame:frame];
    view.backgroundColor = [UIColor clearColor];
    
    if (titleView) {
      [view addSubview:titleView]; 
    }
    if (captionView) {
      [view addSubview:captionView];
    }
    if (imageView) {
      [view addSubview:imageView];
      UIView* imageButtom = [Util tapViewWithFrame:imageView.frame andCallback:^{
        ShowImageViewController* controller = [[[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil] autorelease];
        controller.imageURL = imagePath;
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
      }];
      [view addSubview:imageButtom];
    }
    //TODO
    if (entity.coordinates) {
      NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","]; 
      CLLocationDegrees latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
      CLLocationDegrees longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
      CLLocationCoordinate2D mapCoord = CLLocationCoordinate2DMake(latitude, longitude);
      MKCoordinateSpan mapSpan = MKCoordinateSpanMake(_standardLatLongSpan, _standardLatLongSpan);
      MKCoordinateRegion region = MKCoordinateRegionMake(mapCoord, mapSpan);
      MKMapView* mapView = [[[MKMapView alloc] initWithFrame:CGRectMake(15,CGRectGetMaxY(view.frame), 290, 120)] autorelease];
      mapView.userInteractionEnabled = NO;
      [view addSubview:mapView];
      frame = view.frame;
      frame.size.height = CGRectGetMaxY(mapView.frame);
      view.frame = frame;
      [mapView setRegion:region animated:YES];
      STPlaceAnnotation* annotation = [[[STPlaceAnnotation alloc] initWithLatitude:latitude longitude:longitude] autorelease];
      [mapView addAnnotation:annotation];
      NSString* encodedTitle = [entity.title stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding];
      NSString* url = [NSString stringWithFormat:@"http://www.google.com/maps?q=%@@%@", encodedTitle, entity.coordinates];
      UIView* tapView = [Util tapViewWithFrame:mapView.frame andCallback:^{
        [[STActionManager sharedActionManager] didChooseAction:[STSimpleAction actionWithURLString:url] withContext:[STActionContext context]];
      }];
      [view addSubview:tapView];
    }
    
    [view autorelease];
  }
  return view;
}

@end
