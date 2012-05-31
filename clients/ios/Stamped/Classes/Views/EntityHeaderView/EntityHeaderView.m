//
//  EntityHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "EntityHeaderView.h"
#import "STPlaceAnnotation.h"

#define kLatLongSpan 600.0f / 111000.0f

@implementation EntityHeaderView
@synthesize style=_style;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

    }
    return self;
}

- (CGFloat)height {
    
    return 200.0f;
}

- (void)setupWithEntity:(id<STEntityDetail>)entity {
    if (!entity) return;
    
    UIView* view = nil;
    if (entity) {
        CGFloat padding_h = 15;
        CGFloat maxWidth = 200;
        CGFloat maxImageWidth = 320 - (maxWidth + 3 * padding_h);
        if (_style == STHeaderStyleStamp) {
            maxImageWidth = 200;
        }
        NSString* imagePath = nil;
        if (entity.images && [entity.images count] > 0) {
            id<STImageList> imageList = [entity.images objectAtIndex:0];
            if (imageList.sizes.count > 0) {
                id<STImage> firstImage = [imageList.sizes objectAtIndex:0];
                imagePath = firstImage.url;
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
        if (_style == STHeaderStyleEntity) {
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
            imageView.userInteractionEnabled = YES;
            UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
            [imageView addGestureRecognizer:gesture];
            [gesture release];
        }
        
        //TODO
        if (entity.coordinates) {
            NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","]; 
            CLLocationDegrees latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
            CLLocationDegrees longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
            CLLocationCoordinate2D mapCoord = CLLocationCoordinate2DMake(latitude, longitude);
            MKCoordinateSpan mapSpan = MKCoordinateSpanMake(kLatLongSpan, kLatLongSpan);
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
            //NSString* encodedTitle = [entity.title stringByAddingPercentEscapesUsingEncoding:NSASCIIStringEncoding];
            //NSString* url = [NSString stringWithFormat:@"http://www.google.com/maps?q=%@@%@", encodedTitle, entity.coordinates];
            
            /*
            UIView* tapView = [Util tapViewWithFrame:mapView.frame andCallback:^{
              //  [[STActionManager sharedActionManager] didChooseAction:[STSimpleAction actionWithURLString:url] withContext:[STActionContext context]];
            }];
            [view addSubview:tapView];
            */
            
            UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
            [mapView addGestureRecognizer:gesture];
            [gesture release];
            
        }
        
        [view autorelease];
    
    }
}


#pragma mark - Actions
    
- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    if ([gesture.view isKindOfClass:[UIImageView class]]) {
        
        if ([(id)delegate respondsToSelector:@selector(entityHeaderView:imageViewTapped:)]) {
            [self.delegate entityHeaderView:self imageViewTapped:(UIImageView*)gesture.view];
        }
        
    } else if ([gesture.view isKindOfClass:[MKMapView class]]) {
        
        if ([(id)delegate respondsToSelector:@selector(entityHeaderView:mapViewTapped:)]) {
            [self.delegate entityHeaderView:self mapViewTapped:(MKMapView*)gesture.view];
        }
        
    }
    
}


@end 
