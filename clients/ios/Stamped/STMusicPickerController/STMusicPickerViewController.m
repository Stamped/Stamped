//
//  STMusicPickerViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import "STMusicPickerViewController.h"
#import "STTableViewSectionHeader.h"

@interface STMusicPickerViewController ()
@property(nonatomic,retain) NSArray *dataSource;
@property(nonatomic,retain) NSArray *sectionsDataSource;
@property(nonatomic,assign) STMusicPickerQueryType queryType;
@property(nonatomic,assign) BOOL supportsSections;
@end

@implementation STMusicPickerViewController
@synthesize dataSource;
@synthesize sectionsDataSource;
@synthesize queryType;
@synthesize delegate;
@synthesize supportsSections = _supportsSections;

- (void)commonInit {
    
        
    switch (self.queryType) {
        case STMusicPickerQueryTypeArtist:
            self.title = @"Artists";
            break;
        case STMusicPickerQueryTypeSong:
            self.title = @"Songs";
            break;
        case STMusicPickerQueryTypeAlbum:
            self.title = @"Albums";
            break;
            
        default:
            break;
    }
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        
        MPMediaQuery *query;
        
        switch (self.queryType) {
            case STMusicPickerQueryTypeArtist:
                query = [MPMediaQuery artistsQuery];
                break;
            case STMusicPickerQueryTypeSong:
                query = [MPMediaQuery songsQuery];
                break;
            case STMusicPickerQueryTypeAlbum:
                query = [MPMediaQuery albumsQuery];
                break;
                
            default:
                break;
        }

        /*
         * collectionSections only available > 4.2
        */
        self.supportsSections = [query respondsToSelector:@selector(collectionSections)];
        self.dataSource = (id)query.collections;

        if (self.supportsSections) {
            self.sectionsDataSource = (id)query.collectionSections;
        }
        
        dispatch_async(dispatch_get_main_queue(), ^{
            [self.tableView reloadData];
        });
        
    });
    
}

- (id)initWithQueryType:(STMusicPickerQueryType)type {
    
    if ((self = [super initWithStyle:UITableViewStylePlain])) {

        self.queryType = type;
        [self commonInit];
    
    }
    return self;
    
}

- (id)initWithStyle:(UITableViewStyle)style {
    if ((self = [super initWithStyle:style])) {

        self.queryType = STMusicPickerQueryTypeSong;
        [self commonInit];
        
    }
    return self;
}

- (void)dealloc {
    
    self.delegate = nil;
    self.sectionsDataSource = nil;
    self.dataSource = nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];

    switch (self.queryType) {
        case STMusicPickerQueryTypeArtist:
            self.tableView.rowHeight = 56.0f;
            break;
        case STMusicPickerQueryTypeAlbum:
        case STMusicPickerQueryTypeSong:
        default:
            self.tableView.rowHeight = 64.0f;
            break;
    }
    
}

- (void)viewDidUnload {
    self.dataSource = nil;
    [super viewDidUnload];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    self.dataSource = nil;
}


#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    if (self.supportsSections) {
        return [self.sectionsDataSource count];
    }
    
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    
    if (self.supportsSections) {
        MPMediaQuerySection *sec = [self.sectionsDataSource objectAtIndex:section];
        return [sec range].length;
    }
    
    return [self.dataSource count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"Cell";
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:CellIdentifier] autorelease];
        cell.textLabel.font = [UIFont stampedFontWithSize:20];
        cell.textLabel.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];
    }
    
    
    NSString *artistKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingArtist];
    MPMediaItem *item;
    
    if (self.supportsSections) {
        
        MPMediaQuerySection *sec = [self.sectionsDataSource objectAtIndex:indexPath.section];
        NSInteger index = sec.range.location + indexPath.row;
        item = [[self.dataSource objectAtIndex:index] representativeItem];

    } else {
        
        item = [[self.dataSource objectAtIndex:indexPath.row] representativeItem];
        
    }
    

    switch (self.queryType) {
        case STMusicPickerQueryTypeAlbum: {
            
            NSString *albumKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingAlbum];
            cell.textLabel.text = [item valueForProperty:albumKey];
            cell.detailTextLabel.text = [item valueForProperty:artistKey];
            cell.imageView.image = [UIImage imageNamed:@"entity_create_album.png"];

        }
            
            break;
        case STMusicPickerQueryTypeArtist:
            
            cell.textLabel.text = [item valueForProperty:artistKey];
            cell.imageView.image = [UIImage imageNamed:@"entity_create_artist.png"];

            break;
            
        case STMusicPickerQueryTypeSong: {
            
            NSString *songKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingTitle];
            cell.textLabel.text = [item valueForProperty:songKey];
            cell.detailTextLabel.text = [item valueForProperty:artistKey];
            cell.imageView.image = [UIImage imageNamed:@"entity_create_song.png"];

        }
            break;
        default:
            break;
    }

    return cell;

}

- (NSArray *)sectionIndexTitlesForTableView:(UITableView *)tableView {
    
    if (self.supportsSections) {
        
        NSMutableArray *items = [NSMutableArray arrayWithCapacity:self.sectionsDataSource.count];
        for (MPMediaQuerySection *section in self.sectionsDataSource) {
            [items addObject:section.title];
        }
        return items;
        
    }
    
    return nil;
    
}


#pragma mark - Table view delegate

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    
    if (self.supportsSections) {
        MPMediaQuerySection *sec = [self.sectionsDataSource objectAtIndex:section];
        return sec.title;
    }

    return nil;
        
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    return self.supportsSections ? [STTableViewSectionHeader height] : 0.0f;
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    if (self.supportsSections) {
        NSString *title = [self tableView:tableView titleForHeaderInSection:section];
        STTableViewSectionHeader *view = [[STTableViewSectionHeader alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 0)];
        view.titleLabel.text = title;
        return [view autorelease];
    }
    
    return nil;
    
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {

    MPMediaItem *item;
    
    if (self.supportsSections) {
        
        MPMediaQuerySection *sec = [self.sectionsDataSource objectAtIndex:indexPath.section];
        NSInteger index = sec.range.location + indexPath.row;
        item = [[self.dataSource objectAtIndex:index] representativeItem];
        
    } else {
        
        item = [[self.dataSource objectAtIndex:indexPath.row] representativeItem];
        
    }
    
    if ([(id)delegate respondsToSelector:@selector(stMusicPickerController:didPickMediaItem:)]) {
        [self.delegate stMusicPickerController:self didPickMediaItem:item];
    }
    
}

@end
