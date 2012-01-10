//
//  STPlaceAnnotation.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>

extern const CGFloat kStandardLatLongSpan;

@class Stamp;
@class Entity;

@interface STPlaceAnnotation : NSObject<MKAnnotation> {
@private
  CLLocationDegrees latitude_;
  CLLocationDegrees longitude_;
}

@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, retain) Entity* entityObject;

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude;
@end