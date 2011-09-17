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

@interface SearchEntitiesTableViewCell : UITableViewCell {
 @private  
  SearchEntitiesCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) SearchResult* searchResult;

@end
