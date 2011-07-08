//
//  StampEntity.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/7/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

typedef enum {
  StampEntityTypeBook,
  StampEntityTypeFilm,
  StampEntityTypeMusic,
  StampEntityTypePlace,
  StampEntityTypeOther
} StampEntityType;

@interface StampEntity : NSObject

@property (nonatomic, retain) UIImage* userImage;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* name;
@property (nonatomic, copy) NSString* userName;
@property (nonatomic, copy) NSString* comment;
@property (nonatomic, copy) NSArray* subEntities;
@property (nonatomic) StampEntityType type;

@end