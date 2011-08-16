//
//  STPlaceAnnotation.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STPlaceAnnotation.h"

const CGFloat kStandardLatLongSpan = 400.0f / 111000.0f;

@implementation STPlaceAnnotation

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude {
  self = [super init];
  if (self) {
    latitude_ = latitude;
    longitude_ = longitude;
  }
  return self;
}

- (CLLocationCoordinate2D)coordinate {
  return CLLocationCoordinate2DMake(latitude_, longitude_);
}

@end
