//
//  SearchEntitiesTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Entity;
@class SearchEntitiesCellView;
@class SearchResult;

@interface SearchEntitiesTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) SearchResult* searchResult;

@end
