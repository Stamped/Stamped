//
//  EntityHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import <UIKit/UIKit.h>
#import <CoreLocation/CoreLocation.h>
#import <MapKit/MapKit.h>
#import "STEntityDetail.h"

typedef enum {
    STHeaderStyleEntity = 0,
    STHeaderStyleStamp,
} STHeaderStyle;

@protocol EntityHeaderViewDelegate;
@interface EntityHeaderView : UIView

@property(nonatomic,readonly) STHeaderStyle style;
@property(nonatomic,assign) id <EntityHeaderViewDelegate> delegate;

- (CGFloat)height;
- (void)setupWithEntity:(id<STEntityDetail>)entity;

@end
@protocol EntityHeaderViewDelegate
- (void)entityHeaderView:(EntityHeaderView*)view imageViewTapped:(UIImageView*)imageView;
- (void)entityHeaderView:(EntityHeaderView*)view mapViewTapped:(MKMapView*)mapView;
@end