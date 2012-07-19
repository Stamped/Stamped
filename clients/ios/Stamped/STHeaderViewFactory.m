//
//  STHeaderViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STHeaderViewFactory.h"
#import <CoreText/CoreText.h>
#import <CoreLocation/CoreLocation.h>
#import <MapKit/MapKit.h>
#import "STActionManager.h"
#import "STSimpleAction.h"
#import "STPhotoViewController.h"
#import "STEntityAnnotation.h"
#import "STImageCache.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

static const CGFloat _standardLatLongSpan = 600.0f / 111000.0f;

@interface STHeaderViewFactory ()

@property (nonatomic, readonly, retain) NSString* style;

@end

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

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
    NSString* url = [Util entityImageURLForEntity:anEntityDetail];
    if (url) {
        UIImage* image = [[STImageCache sharedInstance] cachedImageForImageURL:url];
        if (image) {
            return image;
        }
        NSData* data = [[[NSData alloc] initWithContentsOfURL:[NSURL URLWithString:url]] autorelease];
        image = [UIImage imageWithData:data];
        if (image) {
            [[STImageCache sharedInstance] cacheImage:image forImageURL:url];
        }
        return image;
    }
    return nil;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)entity
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
    UIView* view = nil;
    UIImage* image = asyncState;
    if (entity) {
        CGFloat padding_h = 15;
        CGFloat maxWidth = 200;
        CGFloat maxImageWidth = 320 - (maxWidth + 3 * padding_h);
        if ([self.style isEqualToString:@"StampDetail"]) {
            maxImageWidth = 200;
        }
        UIView* imageView = nil;
        CGRect imageFrame = CGRectZero;
        if (image) {
            imageView = [[[UIImageView alloc] initWithImage:image] autorelease];
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
            titleView.clipsToBounds = NO;
            
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
            if ([entity.subcategory isEqualToString:@"app"]) {
                CGFloat coeff = 60 /360.;
                CGFloat radius = imageView.frame.size.width * coeff;
                imageView.layer.cornerRadius = radius;
                imageView.layer.masksToBounds = YES;
                UIView* shadowView = [[[UIView alloc] initWithFrame:imageView.frame] autorelease];
                shadowView.layer.shadowOpacity = .5;
                shadowView.layer.shadowColor = [UIColor blackColor].CGColor;
                shadowView.layer.shadowRadius = 7;
                shadowView.layer.shadowOffset = CGSizeMake(0, shadowView.layer.shadowRadius/2);
                shadowView.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:shadowView.bounds cornerRadius:radius].CGPath;
                [view addSubview:shadowView];
            }
            else {
                imageView.layer.shadowColor = [UIColor blackColor].CGColor;
                imageView.layer.shadowOpacity = .2;
                imageView.layer.shadowRadius = 2.0;
                imageView.layer.shadowOffset = CGSizeMake(0, 2);
                imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;
            }
            [view addSubview:imageView];
            UIView* imageButtom = [Util tapViewWithFrame:imageView.frame andCallback:^{
                STPhotoViewController *controller = [[[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:[Util entityImageURLForEntity:entity]]] autorelease];
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
            
            STEntityAnnotation* annotation = [[[STEntityAnnotation alloc] initWithEntityDetail:entity] autorelease];
            [mapView addAnnotation:annotation];
            /*
             TODO FIX
             STPlaceAnnotation* annotation = [[[STPlaceAnnotation alloc] initWithLatitude:latitude longitude:longitude] autorelease];
             [mapView addAnnotation:annotation];
             */
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
