//
//  STPlaceAnnotation.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <MapKit/MapKit.h>

extern const CGFloat kStandardLatLongSpan;

@interface STPlaceAnnotation : NSObject<MKAnnotation> {
@private
  CLLocationDegrees latitude_;
  CLLocationDegrees longitude_;
}

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude;
@end